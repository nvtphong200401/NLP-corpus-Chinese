#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract and build corpus from djvu.txt file
Creates organized text files with metadata from historical Chinese text
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('djvu_corpus_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DjvuCorpusExtractor:
    """Extract and organize historical text corpus from djvu.txt file"""
    
    def __init__(self, input_file: str, output_dir: str = "ming_history_txt_files"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.metadata = {}
        self.chapters = []
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from the file content"""
        metadata = {}
        
        # Extract title from filename
        filename = self.input_file.name
        if "白话资治通鉴" in filename:
            metadata['title'] = "白话资治通鉴"
        
        # Extract volume information from filename
        volume_match = re.search(r'(\d+)', filename)
        if volume_match:
            metadata['volume'] = f"第{volume_match.group(1)}册"
        else:
            metadata['volume'] = "第1册"
            
        # Period covered (from filename)
        period_match = re.search(r'周威烈王二十三年.*?汉惠帝七', filename)
        if period_match:
            metadata['period'] = period_match.group(0)
        
        # Extract authors/editors from content
        authors = []
        editors = []
        
        # Look for main editors (主编)
        main_editor_pattern = r'主编[：:\s]*([^副\n]+)'
        main_editor_match = re.search(main_editor_pattern, content)
        if main_editor_match:
            editors_text = main_editor_match.group(1).strip()
            # Clean up and split
            editors_text = re.sub(r'["""\s]+', ' ', editors_text)
            main_editors = re.split(r'[\s,，]+', editors_text)
            editors.extend([ed.strip() for ed in main_editors if ed.strip()])
        
        # Look for deputy editors (副主编)
        deputy_editor_pattern = r'副主编[：:\s]*([^\n]+)'
        deputy_editor_match = re.search(deputy_editor_pattern, content)
        if deputy_editor_match:
            deputy_text = deputy_editor_match.group(1).strip()
            deputy_text = re.sub(r'["""\s]+', ' ', deputy_text)
            deputy_editors = re.split(r'[\s,，]+', deputy_text)
            editors.extend([ed.strip() for ed in deputy_editors if ed.strip()])
        
        # Clean up editors list
        editors = [ed for ed in editors if ed and len(ed) > 1 and not re.match(r'^[:\s"]+$', ed)]
        
        metadata['editors'] = ', '.join(editors[:6])  # Limit to first 6 editors
        
        # Extract publisher information
        publisher_info = []
        
        # Look for publisher
        publisher_patterns = [
            r'中华书局出版',
            r'新华书店.*?发行',
            r'北京第二新华印刷厂印刷'
        ]
        
        for pattern in publisher_patterns:
            if re.search(pattern, content):
                match = re.search(pattern, content)
                if match:
                    publisher_info.append(match.group(0))
        
        metadata['publisher'] = '; '.join(publisher_info) if publisher_info else '中华书局出版'
        
        # Extract publication date
        date_pattern = r'1993.*?年.*?月.*?第.*?版'
        date_match = re.search(date_pattern, content)
        if date_match:
            metadata['publication_date'] = date_match.group(0)
        else:
            metadata['publication_date'] = '1993年3月第1版'
        
        # Extract source description
        metadata['source'] = '白话资治通鉴djvu扫描版'
        
        return metadata
    
    def find_content_start(self, lines: List[str]) -> int:
        """Find where the actual historical content starts"""
        for i, line in enumerate(lines):
            # Look for the start of the first volume
            if '资治通鉴第一卷' in line or ('周纪一' in line and '威烈王' in line):
                return i
            # Alternative pattern - look for volume headers
            if re.search(r'第.*卷.*周纪.*威烈王', line):
                return i
          # If we can't find the exact start, look for content patterns
        for i, line in enumerate(lines):
            if re.search(r'周威烈王.*年.*公元前', line):
                return max(0, i - 5)  # Start a few lines before
        
        return len(lines) // 3  # Fallback: assume content starts after first third
    
    def extract_chapters(self, content: str) -> List[Dict]:
        """Extract individual chapters/sections from the content"""
        lines = content.split('\n')
        content_start = self.find_content_start(lines)
        content_lines = lines[content_start:]
        
        chapters = []
        
        # Look for the 12 main volumes as mentioned in table of contents
        # Pattern: 第X卷 followed by dynasty name (周纪, 秦纪, 汉纪)
        volume_patterns = [
            r'第\s*([一二三四五六七八九十]+)\s*卷\s*["""]?\s*(周纪[一二三四五六七八九十]*)',
            r'第\s*([一二三四五六七八九十]+)\s*卷\s*["""]?\s*(秦纪[一二三四五六七八九十]*)',
            r'第\s*([一二三四五六七八九十]+)\s*卷\s*["""]?\s*(汉纪[一二三四五六七八九十]*)'
        ]
        
        # Find main chapter boundaries
        chapter_boundaries = []
        
        for i, line in enumerate(content_lines):
            for pattern in volume_patterns:
                match = re.search(pattern, line)
                if match:
                    volume_num = match.group(1)
                    dynasty_era = match.group(2)
                    
                    # Convert Chinese numerals to Arabic
                    chinese_to_arabic = {
                        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
                        '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12
                    }
                    
                    chapter_num = chinese_to_arabic.get(volume_num, len(chapter_boundaries) + 1)
                    
                    # Extract page number if present in the line or nearby lines
                    page_num = ""
                    # Look for page numbers in current and surrounding lines
                    search_lines = content_lines[max(0, i-2):i+3]
                    for search_line in search_lines:
                        page_match = re.search(r'(\d+)', search_line)
                        if page_match and len(page_match.group(1)) <= 3:  # Reasonable page number
                            page_num = page_match.group(1)
                            break
                    
                    if not page_num:
                        page_num = str(i + 1)  # Fallback to line number
                    
                    chapter_boundaries.append({
                        'start_idx': i,
                        'chapter_num': chapter_num,
                        'title': dynasty_era,
                        'page_num': page_num,
                        'full_title': line.strip()
                    })
                    break
        
        # If we found fewer than expected, look for simpler patterns
        if len(chapter_boundaries) < 8:
            logger.warning(f"Only found {len(chapter_boundaries)} main chapters, looking for simpler patterns")
            
            # Look for dynasty era markers without volume numbers
            simple_patterns = [
                r'(周纪[一二三四五六七八九十]*)',
                r'(秦纪[一二三四五六七八九十]*)',
                r'(汉纪[一二三四五六七八九十]*)'
            ]
            
            for i, line in enumerate(content_lines):
                for pattern in simple_patterns:
                    match = re.search(pattern, line)
                    if match and len(line.strip()) < 100:  # Likely a chapter header
                        dynasty_era = match.group(1)
                        
                        # Avoid duplicates
                        if not any(cb['title'] == dynasty_era for cb in chapter_boundaries):
                            # Extract page number
                            page_num = ""
                            search_lines = content_lines[max(0, i-2):i+3]
                            for search_line in search_lines:
                                page_match = re.search(r'(\d+)', search_line)
                                if page_match and len(page_match.group(1)) <= 3:
                                    page_num = page_match.group(1)
                                    break
                            
                            if not page_num:
                                page_num = str(len(chapter_boundaries) + 1)
                            
                            chapter_boundaries.append({
                                'start_idx': i,
                                'chapter_num': len(chapter_boundaries) + 1,
                                'title': dynasty_era,
                                'page_num': page_num,
                                'full_title': line.strip()
                            })
                        break
        
        # Sort by start index
        chapter_boundaries.sort(key=lambda x: x['start_idx'])
        
        # Extract chapter content
        for i, boundary in enumerate(chapter_boundaries):
            start_idx = boundary['start_idx']
            end_idx = chapter_boundaries[i + 1]['start_idx'] if i + 1 < len(chapter_boundaries) else len(content_lines)
            
            chapter_lines = content_lines[start_idx:end_idx]
            chapter_text = '\n'.join(chapter_lines).strip()
            
            if len(chapter_text) < 500:  # Skip very short sections
                continue
            
            # Extract time period if available
            period = ""
            period_match = re.search(r'前\s*\d+.*?年', chapter_text[:300])
            if period_match:
                period = period_match.group(0)
            
            chapter_info = {
                'index': boundary['chapter_num'],
                'page_num': boundary['page_num'],
                'title': boundary['title'],
                'period': period,
                'content': chapter_text,
                'length': len(chapter_text),
                'full_title': boundary['full_title']
            }
            
            chapters.append(chapter_info)
        
        # If still no good chapters found, create based on content division
        if len(chapters) < 6:
            logger.warning("Creating chapters based on content division as fallback")
            section_size = len(content_lines) // 12  # Target 12 chapters
            
            chapters = []
            chapter_names = [
                "周纪一", "周纪二", "周纪三", "周纪四", "周纪五",
                "秦纪一", "秦纪二", "秦纪三",
                "汉纪一", "汉纪二", "汉纪三", "汉纪四"
            ]
            
            for i in range(12):
                start_idx = i * section_size
                end_idx = min((i + 1) * section_size, len(content_lines))
                
                chapter_lines = content_lines[start_idx:end_idx]
                chapter_text = '\n'.join(chapter_lines).strip()
                
                if len(chapter_text) < 100:
                    continue
                
                chapter_info = {
                    'index': i + 1,
                    'page_num': str((i * 20) + 1),  # Estimated page numbers
                    'title': chapter_names[i] if i < len(chapter_names) else f"第{i+1}章",
                    'period': f"第{i+1}册内容",
                    'content': chapter_text,
                    'length': len(chapter_text),
                    'full_title': chapter_names[i] if i < len(chapter_names) else f"第{i+1}章"
                }
                
                chapters.append(chapter_info)
        
        return chapters
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and other artifacts
        text = re.sub(r'\(\d+\)', '', text)
        text = re.sub(r'第.*?页', '', text)        
        # Clean up punctuation
        text = re.sub(r'\s*([，。；：！？])\s*', r'\1', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[,，]{2,}', '，', text)
        text = re.sub(r'[.。]{2,}', '。', text)
        
        return text.strip()
    
    def create_filename(self, metadata: Dict, chapter_info: Dict) -> str:
        """Create filename in format: <page_number>_<chapter_number>_<title>.txt"""
        # Get page number
        page_num = chapter_info.get('page_num', '001')
        
        # Get chapter number with zero padding
        chapter_num = f"{chapter_info['index']:02d}"
        
        # Clean up chapter title for filename
        title = chapter_info['title']
        
        # Remove any invalid filename characters
        title = re.sub(r'[<>:"/\\|?*]', '_', title)
        title = re.sub(r'\s+', '_', title)
        
        filename = f"{page_num}_{chapter_num}_{title}.txt"
        
        return filename
        chapter_title = chapter_info['title']
        
        # Extract meaningful title from the chapter content
        # Look for patterns like "周纪一", "汉纪三", etc.
        title_patterns = [
            r'(周纪[一二三四五六七八九十]+)',
            r'(秦纪[一二三四五六七八九十]+)', 
            r'(汉纪[一二三四五六七八九十]+)',
            r'第.*?卷.*?(周纪.*?)[\s""]',
            r'第.*?卷.*?(秦纪.*?)[\s""]',
            r'第.*?卷.*?(汉纪.*?)[\s""]'
        ]
        
        clean_title = ""
        for pattern in title_patterns:
            match = re.search(pattern, chapter_title)
            if match:
                clean_title = match.group(1)
                break
        
        # If no pattern found, use a cleaned version of the title
        if not clean_title:
            clean_title = re.sub(r'[^\w\u4e00-\u9fff]', '', chapter_title[:20])
            if not clean_title:
                clean_title = f"章节{chapter_num}"
        
        # Remove any remaining invalid filename characters
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', clean_title)
        
        filename = f"{chapter_num}_{clean_title}.txt"
        
        return filename
    
    def save_chapter(self, chapter_info: Dict, metadata: Dict) -> str:
        """Save individual chapter to file"""
        filename = self.create_filename(metadata, chapter_info)
        filepath = self.output_dir / filename
        
        # Prepare content with metadata header
        content_parts = []
        
        # Add metadata header
        content_parts.append("=" * 50)
        content_parts.append("文档元数据 (Document Metadata)")
        content_parts.append("=" * 50)
        content_parts.append(f"标题: {metadata.get('title', 'N/A')}")
        content_parts.append(f"卷册: {metadata.get('volume', 'N/A')}")
        content_parts.append(f"时期: {metadata.get('period', 'N/A')}")
        content_parts.append(f"章节: {chapter_info['title']}")
        content_parts.append(f"编者: {metadata.get('editors', 'N/A')}")
        content_parts.append(f"出版社: {metadata.get('publisher', 'N/A')}")
        content_parts.append(f"出版日期: {metadata.get('publication_date', 'N/A')}")
        content_parts.append(f"来源: {metadata.get('source', 'N/A')}")
        content_parts.append("")
        content_parts.append("=" * 50)
        content_parts.append("正文内容 (Main Content)")
        content_parts.append("=" * 50)
        content_parts.append("")
        
        # Clean and add main content
        cleaned_content = self.clean_text(chapter_info['content'])
        content_parts.append(cleaned_content)
        
        # Write to file
        full_content = '\n'.join(content_parts)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Saved chapter: {filename} ({len(cleaned_content)} characters)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving chapter {filename}: {e}")
            return ""
    
    def create_summary_file(self, metadata: Dict, chapters: List[Dict]) -> str:
        """Create a summary file with corpus information"""
        summary_file = self.output_dir / "corpus_summary.txt"
        
        summary_parts = []
        summary_parts.append("白话资治通鉴语料库总结")
        summary_parts.append("=" * 40)
        summary_parts.append("")
        
        # Corpus metadata
        summary_parts.append("语料库元数据:")
        for key, value in metadata.items():
            summary_parts.append(f"  {key}: {value}")
        summary_parts.append("")
        
        # Chapter summary
        summary_parts.append(f"章节总数: {len(chapters)}")
        summary_parts.append(f"总字符数: {sum(ch['length'] for ch in chapters):,}")
        summary_parts.append("")
        
        # Chapter list
        summary_parts.append("章节列表:")
        for i, chapter in enumerate(chapters, 1):
            summary_parts.append(f"  {i:2d}. {chapter['title'][:30]} ({chapter['length']:,} 字符)")
        
        summary_content = '\n'.join(summary_parts)
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"Created summary file: {summary_file}")
            return str(summary_file)
            
        except Exception as e:
            logger.error(f"Error creating summary file: {e}")
            return ""
    
    def extract_corpus(self) -> bool:
        """Main method to extract and organize the corpus"""
        try:
            logger.info(f"Starting corpus extraction from: {self.input_file}")
            
            # Read input file
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read file: {len(content):,} characters")
            
            # Extract metadata
            self.metadata = self.extract_metadata(content)
            logger.info(f"Extracted metadata: {self.metadata}")
            
            # Extract chapters
            self.chapters = self.extract_chapters(content)
            logger.info(f"Extracted {len(self.chapters)} chapters")
            
            # Save chapters
            saved_files = []
            for chapter in self.chapters:
                filepath = self.save_chapter(chapter, self.metadata)
                if filepath:
                    saved_files.append(filepath)
            
            # Create summary
            summary_file = self.create_summary_file(self.metadata, self.chapters)
            if summary_file:
                saved_files.append(summary_file)
            
            logger.info(f"Successfully extracted corpus: {len(saved_files)} files created")
            return True
            
        except Exception as e:
            logger.error(f"Error during corpus extraction: {e}")
            return False

def main():
    """Main execution function"""
    # File path
    input_file = r"c:\Users\nguyenphong\Downloads\study master\NLP\06.Minh Sử_MinhNguyen\06.Minh Sử\白话资治通鉴01—周威烈王二十三年.至.汉惠帝七_djvu.txt"
    
    # Create extractor
    extractor = DjvuCorpusExtractor(input_file)
    
    # Extract corpus
    success = extractor.extract_corpus()
    
    if success:
        print(f"\n✅ Corpus extraction completed successfully!")
        print(f"📁 Output directory: {extractor.output_dir.absolute()}")
        print(f"📊 Chapters extracted: {len(extractor.chapters)}")
        print(f"📄 Total files created: {len(list(extractor.output_dir.glob('*.txt')))}")
    else:
        print("\n❌ Corpus extraction failed. Check the log for details.")

if __name__ == "__main__":
    main()
