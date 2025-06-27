# Zizhi Tongjian XML Corpus Extractor

This project extracts and organizes content from the "白话资治通鉴" (Modern Chinese Translation of Zizhi Tongjian) into a structured XML corpus format suitable for NLP and historical text analysis.

## Overview

The Zizhi Tongjian (资治通鉴) is one of China's most important historical texts, originally compiled by Sima Guang during the Northern Song Dynasty. This tool processes the modern Chinese translation to create a structured corpus with hierarchical metadata.

## File Structure

- `extract_zizhi_tongjian_xml.py` - Main extraction script
- `example_zizhi_tongjian_usage.py` - Example usage and analysis
- `白话资治通鉴01—周威烈王二十三年.至.汉惠帝七_djvu.txt` - Input text file
- `zizhi_tongjian_corpus.xml` - Output XML corpus (generated)

## XML Structure

The extracted corpus follows this hierarchical structure:

```xml
<corpus>
  <metadata>
    <title>白话资治通鉴</title>
    <volume>第一册</volume>
    <original_author>司马光</original_author>
    <translator>沈志华等</translator>
    <period>前403年-前182年</period>
    <language>现代汉语</language>
    <extraction_date>2025-06-22T...</extraction_date>
  </metadata>
  
  <sections>
    <section id="周纪一">
      <section_name>周纪一</section_name>
      
      <page id="周威烈王二十三年">
        <page_name>周威烈王二十三年</page_name>
        <year>前403年</year>
        
        <sentence id="s_000001" type="narrative">
          周威烈王姬午首次分封晋国大夫魏斯、赵籍、韩虑为诸侯国
        </sentence>
        
        <sentence id="s_000002" type="commentary">
          臣司马光曰：我知道天子的职责中最重要的是维护礼...
        </sentence>
        
        <!-- More sentences... -->
      </page>
      
      <!-- More pages... -->
    </section>
    
    <!-- More sections... -->
  </sections>
</corpus>
```

## Metadata Fields

- **title**: 白话资治通鉴 (Modern Chinese Zizhi Tongjian)
- **volume**: Volume number (第一册)
- **original_author**: 司马光 (Sima Guang)
- **translator**: 沈志华等 (Shen Zhihua et al.)
- **period**: Historical period covered (前403年-前182年)
- **language**: 现代汉语 (Modern Chinese)

## Hierarchical Structure

### Sections (章节)
- **Section ID**: Based on dynasty chronicles (e.g., "周纪一", "汉纪一")
- **Section Name**: Full chronicle names

### Pages (页面)
- **Page ID**: Year-based identifiers (e.g., "周威烈王二十三年")
- **Page Name**: Specific year descriptions with ruler information
- **Year**: Extracted temporal information

### Sentences (句子)
- **Sentence ID**: Sequential numbering (s_000001, s_000002, etc.)
- **Sentence Type**: 
  - `narrative`: Regular historical narrative
  - `commentary`: Commentary by Sima Guang (臣司马光曰)
- **Content**: Individual historical events and information

## Usage

### Basic Extraction

```python
from extract_zizhi_tongjian_xml import ZizhiTongjianXMLExtractor

# Create extractor
extractor = ZizhiTongjianXMLExtractor(
    input_file="白话资治通鉴01—周威烈王二十三年.至.汉惠帝七_djvu.txt",
    output_file="zizhi_tongjian_corpus.xml"
)

# Run extraction
extractor.extract_to_xml()

# Get statistics
stats = extractor.generate_statistics()
print(stats)
```

### Command Line Usage

```bash
# Run the extraction
python extract_zizhi_tongjian_xml.py

# Run example with analysis
python example_zizhi_tongjian_usage.py
```

### Analysis and Search

```python
import xml.etree.ElementTree as ET

# Load corpus
tree = ET.parse("zizhi_tongjian_corpus.xml")
root = tree.getroot()

# Get all narrative sentences
narratives = root.findall(".//sentence[@type='narrative']")

# Get all commentary sentences  
commentaries = root.findall(".//sentence[@type='commentary']")

# Search for specific content
for sentence in root.findall(".//sentence"):
    if "周威烈王" in (sentence.text or ""):
        print(f"Found: {sentence.text}")
```

## Features

- **Automatic Structure Detection**: Identifies dynasty chronicles, years, and content types
- **Metadata Extraction**: Extracts temporal and authorial information
- **Content Classification**: Distinguishes between narrative and commentary
- **Chinese Text Processing**: Handles traditional Chinese date formats and punctuation
- **XML Output**: Well-formed XML with proper encoding and structure
- **Statistics Generation**: Provides extraction statistics and corpus overview
- **Search Functionality**: Built-in search and analysis capabilities

## Requirements

**Important**: This script requires the `tsflow-env` conda environment to be activated before running.

### Python Dependencies
```
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
```

### System Requirements
- Python 3.7+
- Conda package manager
- Windows/Linux/macOS

## Installation

1. **Activate the conda environment**:
```bash
conda activate tsflow-env
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Place the input file in the same directory**:
- `白话资治通鉴01—周威烈王二十三年.至.汉惠帝七_djvu.txt`

4. **Run the extraction**:
```bash
# Option 1: Use the batch script (Windows)
run_extraction.bat

# Option 2: Run directly
python extract_zizhi_tongjian_xml.py

# Option 3: Run with examples and analysis
python example_zizhi_tongjian_usage.py
```

## Output Files

- `zizhi_tongjian_corpus.xml` - Main XML corpus file
- `zizhi_tongjian_corpus.formatted.xml` - Human-readable formatted version
- `zizhi_tongjian_extraction.log` - Extraction log file

## Historical Context

The corpus covers the period from 403 BCE to 182 BCE, including:

- **Warring States Period** (战国时代): Political fragmentation and philosophical development
- **Qin Dynasty** (秦朝): Unification under the First Emperor
- **Early Han Dynasty** (汉朝): Establishment of the Han imperial system

This makes it valuable for studying:
- Classical Chinese political thought
- Historical narrative techniques
- Evolution of Chinese administrative systems
- Biographical writing traditions

## Applications

This structured corpus can be used for:

- **Historical Text Analysis**: Study narrative patterns and themes
- **Named Entity Recognition**: Extract historical figures, places, and events
- **Temporal Analysis**: Track events chronologically
- **Linguistic Studies**: Analyze classical vs. modern Chinese language
- **Digital Humanities**: Create interactive historical timelines
- **Machine Learning**: Train models on historical Chinese text

## License

This tool is for academic and research purposes. The original Zizhi Tongjian text is in the public domain, and the modern translation rights belong to the respective publishers.
