#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of the Zizhi Tongjian XML extractor
Demonstrates how to extract and analyze the corpus

IMPORTANT: Make sure to activate the tsflow-env conda environment first:
conda activate tsflow-env
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from extract_zizhi_tongjian_xml import ZizhiTongjianXMLExtractor

def check_environment():
    """Check if we're in the correct conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'tsflow-env':
        print(f"Warning: Current conda environment is '{conda_env}'")
        print("Please activate the tsflow-env environment first:")
        print("Command: conda activate tsflow-env")
        return False
    else:
        print(f"✓ Using conda environment: {conda_env}")
        return True

def run_extraction():
    """Run the main extraction process"""
    # Check environment first
    if not check_environment():
        return False
        
    input_file = "白话资治通鉴01—周威烈王二十三年.至.汉惠帝七_djvu.txt"
    output_file = "zizhi_tongjian_corpus.xml"
    
    print("Starting Zizhi Tongjian corpus extraction...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    # Create and run extractor
    extractor = ZizhiTongjianXMLExtractor(input_file, output_file)
    extractor.extract_to_xml()
    
    # Generate statistics
    stats = extractor.generate_statistics()
    print("\n=== Extraction Statistics ===")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    return True
    
    return output_file

def analyze_corpus(xml_file):
    """Analyze the extracted XML corpus"""
    if not Path(xml_file).exists():
        print(f"XML file not found: {xml_file}")
        return
    
    print(f"\n=== Analyzing Corpus: {xml_file} ===")
    
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Display metadata
    print("\n--- Metadata ---")
    metadata = root.find("metadata")
    if metadata is not None:
        for child in metadata:
            print(f"{child.tag}: {child.text}")
    
    # Display structure overview
    print("\n--- Structure Overview ---")
    sections = root.find("sections")
    if sections is not None:
        for i, section in enumerate(sections.findall("section"), 1):
            section_name = section.find("section_name")
            pages = section.findall("page")
            sentences = section.findall(".//sentence")
            
            print(f"Section {i}: {section_name.text if section_name is not None else 'Unknown'}")
            print(f"  Pages: {len(pages)}")
            print(f"  Sentences: {len(sentences)}")
            
            # Show first few pages
            for j, page in enumerate(pages[:3], 1):
                page_name = page.find("page_name")
                page_sentences = page.findall("sentence")
                print(f"    Page {j}: {page_name.text if page_name is not None else 'Unknown'} ({len(page_sentences)} sentences)")
            
            if len(pages) > 3:
                print(f"    ... and {len(pages) - 3} more pages")
            print()

def sample_content(xml_file, num_samples=5):
    """Display sample content from the corpus"""
    if not Path(xml_file).exists():
        print(f"XML file not found: {xml_file}")
        return
    
    print(f"\n=== Sample Content (showing {num_samples} sentences) ===")
    
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Get sample sentences
    sentences = root.findall(".//sentence")
    
    for i, sentence in enumerate(sentences[:num_samples], 1):
        sentence_id = sentence.get("id", "unknown")
        sentence_type = sentence.get("type", "unknown")
        text = sentence.text or ""
        
        print(f"{i}. [{sentence_id}] ({sentence_type})")
        print(f"   {text}")
        print()

def search_content(xml_file, search_term):
    """Search for specific content in the corpus"""
    if not Path(xml_file).exists():
        print(f"XML file not found: {xml_file}")
        return
    
    print(f"\n=== Searching for: '{search_term}' ===")
    
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Search sentences
    sentences = root.findall(".//sentence")
    matches = []
    
    for sentence in sentences:
        text = sentence.text or ""
        if search_term in text:
            matches.append(sentence)
    
    print(f"Found {len(matches)} matches:")
    
    for i, sentence in enumerate(matches[:10], 1):  # Show first 10 matches
        sentence_id = sentence.get("id", "unknown")
        sentence_type = sentence.get("type", "unknown")
        text = sentence.text or ""
        
        # Highlight search term
        highlighted_text = text.replace(search_term, f"**{search_term}**")
        
        print(f"{i}. [{sentence_id}] ({sentence_type})")
        print(f"   {highlighted_text}")
        print()
    
    if len(matches) > 10:
        print(f"... and {len(matches) - 10} more matches")

def main():
    """Main example function"""
    print("=== Zizhi Tongjian XML Corpus Extractor Example ===")
    
    # 1. Run extraction
    if not run_extraction():
        print("Extraction failed. Please check the environment and try again.")
        return
    
    xml_file = "zizhi_tongjian_corpus.xml"
    
    # 2. Analyze corpus
    analyze_corpus(xml_file)
    
    # 3. Show sample content
    sample_content(xml_file, 5)
    
    # 4. Example searches
    search_terms = ["周威烈王", "司马光", "前403年"]
    for term in search_terms:
        search_content(xml_file, term)

if __name__ == "__main__":
    main()
