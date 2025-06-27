#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract and organize Zizhi Tongjian corpus into XML format
Creates structured XML corpus from historical Chinese text
"""

import os
import re
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zizhi_tongjian_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZizhiTongjianXMLExtractor:
    """Extract and organize Zizhi Tongjian corpus into XML format"""
    
    def __init__(self, input_file: str, output_file: str = "zizhi_tongjian_corpus.xml"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.root = None
        self.current_section = None
        self.current_page = None
        self.sentence_counter = 0
        
    def create_xml_structure(self) -> ET.Element:
        """Create the root XML structure with metadata"""
        root = ET.Element("corpus")
        
        # Add metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "title").text = "白话资治通鉴"
        ET.SubElement(metadata, "volume").text = "第一册"
        ET.SubElement(metadata, "original_author").text = "司马光"
        ET.SubElement(metadata, "translator").text = "沈志华等"
        ET.SubElement(metadata, "period").text = "前403年-前182年"
        ET.SubElement(metadata, "language").text = "现代汉语"
        ET.SubElement(metadata, "extraction_date").text = datetime.now().isoformat()
        
        # Add sections container
        ET.SubElement(root, "sections")
        
        return root
    
    def extract_year_from_text(self, text: str) -> Optional[str]:
        """Extract year information from text"""
        # Pattern for Chinese traditional year format
        year_patterns = [
            r'([周汉魏晋]{1,2}[纪]{1}[一二三四五六七八九十]{1,3})',  # Dynasty chronicles
            r'(前\d+年)',  # BCE years
            r'([周汉魏晋]{1,2}[王帝][^年]{0,10}[一二三四五六七八九十]{1,3}年)',  # Reign years
            r'([周汉魏晋]{1,2}[王帝][^年]{0,15}元年)',  # First year of reign
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def is_section_header(self, line: str) -> bool:
        """Check if line is a section header (dynasty chronicle)"""
        section_patterns = [
            r'^[周汉魏晋]{1,2}纪[一二三四五六七八九十]{1,3}$',
            r'^第[一二三四五六七八九十]{1,3}章',
        ]
        
        for pattern in section_patterns:
            if re.match(pattern, line.strip()):
                return True
        return False
    
    def is_year_header(self, line: str) -> bool:
        """Check if line is a year header"""
        year_patterns = [
            r'^[周汉魏晋]{1,2}[王帝][^年]{0,15}[一二三四五六七八九十]{1,3}年',
            r'^前\d+年',
            r'^[周汉魏晋]{1,2}[王帝][^年]{0,15}元年',
        ]
        
        for pattern in year_patterns:
            if re.match(pattern, line.strip()):
                return True
        return False
    
    def is_commentary(self, line: str) -> bool:
        """Check if line is a commentary by Sima Guang"""
        return line.strip().startswith('臣司马光曰') or line.strip().startswith('臣光曰')
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and other artifacts
        text = re.sub(r'\d+\s*$', '', text)
        text = re.sub(r'^\s*\d+\s*', '', text)
        return text.strip()
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences based on Chinese punctuation"""
        # Chinese sentence endings
        sentence_endings = r'[。！？；]'
        sentences = re.split(sentence_endings, text)
        
        # Clean and filter empty sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = self.clean_text(sentence)
            if sentence and len(sentence) > 3:  # Filter very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def add_sentence(self, text: str, sentence_type: str = "narrative") -> None:
        """Add a sentence to the current page"""
        if self.current_page is None:
            return
        
        sentences = self.split_into_sentences(text)
        
        for sentence_text in sentences:
            if not sentence_text:
                continue
                
            self.sentence_counter += 1
            sentence_elem = ET.SubElement(self.current_page, "sentence")
            sentence_elem.set("id", f"s_{self.sentence_counter:06d}")
            sentence_elem.set("type", sentence_type)
            sentence_elem.text = sentence_text
    
    def process_content(self) -> None:
        """Process the main content of the file"""
        logger.info(f"Processing file: {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return
        
        lines = content.split('\n')
        in_content_section = False
        current_year = None
        
        # Find where actual content starts (after table of contents)
        content_start_patterns = [
            r'周纪一',
            r'周威烈王',
            r'前403年',
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if we've reached the actual content
            if not in_content_section:
                for pattern in content_start_patterns:
                    if re.search(pattern, line):
                        in_content_section = True
                        logger.info(f"Found content start at line {i}: {line}")
                        break
                if not in_content_section:
                    continue
            
            # Process section headers
            if self.is_section_header(line):
                logger.info(f"Found section: {line}")
                sections_elem = self.root.find("sections")
                self.current_section = ET.SubElement(sections_elem, "section")
                section_id = re.sub(r'[^\w]', '_', line)
                self.current_section.set("id", section_id)
                ET.SubElement(self.current_section, "section_name").text = line
                self.current_page = None
                continue
            
            # Process year headers (pages)
            if self.is_year_header(line):
                logger.info(f"Found year: {line}")
                current_year = line
                if self.current_section is not None:
                    self.current_page = ET.SubElement(self.current_section, "page")
                    page_id = re.sub(r'[^\w]', '_', line)
                    self.current_page.set("id", page_id)
                    ET.SubElement(self.current_page, "page_name").text = line
                    
                    # Extract and add year metadata
                    year_info = self.extract_year_from_text(line)
                    if year_info:
                        ET.SubElement(self.current_page, "year").text = year_info
                continue
            
            # Process commentary
            if self.is_commentary(line):
                self.add_sentence(line, "commentary")
                continue
            
            # Process regular content
            if self.current_page is not None and line:
                # Skip table of contents lines
                if re.match(r'^\d+\s*$', line) or line.startswith('目录') or line.startswith('…'):
                    continue
                
                self.add_sentence(line, "narrative")
    
    def extract_to_xml(self) -> None:
        """Main extraction method"""
        logger.info("Starting Zizhi Tongjian XML extraction")
        
        # Create XML structure
        self.root = self.create_xml_structure()
        
        # Process content
        self.process_content()
        
        # Save XML file
        self.save_xml()
        
        logger.info(f"Extraction completed. XML saved to: {self.output_file}")
    
    def save_xml(self) -> None:
        """Save the XML tree to file"""
        try:
            # Pretty print the XML
            self.indent_xml(self.root)
            
            # Create the tree and write to file
            tree = ET.ElementTree(self.root)
            tree.write(self.output_file, encoding='utf-8', xml_declaration=True)
            
            # Also save a human-readable version
            readable_file = self.output_file.with_suffix('.formatted.xml')
            with open(readable_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write(ET.tostring(self.root, encoding='unicode'))
            
            logger.info(f"XML saved to: {self.output_file}")
            logger.info(f"Formatted XML saved to: {readable_file}")
            
        except Exception as e:
            logger.error(f"Error saving XML: {e}")
    
    def indent_xml(self, elem, level=0):
        """Add indentation to XML for pretty printing"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def generate_statistics(self) -> Dict[str, int]:
        """Generate statistics about the extracted corpus"""
        if self.root is None:
            return {}
        
        stats = {
            'sections': len(self.root.find("sections")),
            'pages': len(self.root.findall(".//page")),
            'sentences': len(self.root.findall(".//sentence")),
            'narrative_sentences': len(self.root.findall(".//sentence[@type='narrative']")),
            'commentary_sentences': len(self.root.findall(".//sentence[@type='commentary']")),
        }
        
        return stats

def check_environment():
    """Check if we're in the correct conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'tsflow-env':
        logger.warning(f"Current conda environment: {conda_env}")
        logger.warning("Please activate the tsflow-env environment first:")
        logger.warning("Run: conda activate tsflow-env")
        return False
    else:
        logger.info(f"Using conda environment: {conda_env}")
        return True

def main():
    """Main function to run the extraction"""
    # Check environment
    if not check_environment():
        logger.error("Please activate the tsflow-env conda environment before running this script")
        logger.error("Command: conda activate tsflow-env")
        return
    
    input_file = "白话资治通鉴01—周威烈王二十三年.至.汉惠帝七_djvu.txt"
    output_file = "zizhi_tongjian_corpus.xml"
    
    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        return
    
    # Create extractor and run extraction
    extractor = ZizhiTongjianXMLExtractor(input_file, output_file)
    extractor.extract_to_xml()
    
    # Generate and display statistics
    stats = extractor.generate_statistics()
    logger.info("Extraction Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    main()
