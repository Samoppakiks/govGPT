"""import unstructured
from unstructured.partition.auto import partition

elements = partition(
    "/Users/saumya/Downloads/RajasthanLandRevenueConversionRules1992.pdf")
print("\n\n".join([str(el) for el in elements]))"""



#old chunker with nltk 
"""from nltk.tokenize import sent_tokenize
import nltk
nltk.download('punkt')"""

"""def split_sections(text):
    # Split the text into sections based on rule numbers
    pattern = r'(\d+\.\s*\w*\.?)'
    sections = re.split(pattern, text)

    combined_sections = []
    for i in range(0, len(sections)-1, 2):
        combined_sections.append(sections[i] + sections[i+1])

    return combined_sections


def split_chunks(sections, max_chunk_size=300, overlap=50):
    chunks = []
    for section in sections:
        section = section.replace('\n', ' ').strip()
        section_length = len(section)

        if section_length <= max_chunk_size:
            # If the section fits into the max_chunk_size, keep it as it is
            chunks.append(section)
        else:
            # If the section is too big, split it into smaller chunks based on sentences
            sentences = sent_tokenize(section)
            tokens = []
            for sentence in sentences:
                tokens.extend(sentence.split())

            for i in range(0, len(tokens), max_chunk_size - overlap):
                start = max(0, i - overlap) if i > 0 else i
                end = min(i + max_chunk_size, len(tokens))
                small_chunk = ' '.join(tokens[start:end])
                chunks.append(small_chunk)

    total_chunks = len(chunks)
    print(f"Total number of chunks created: {total_chunks}")
    return chunks


def split_text(text, max_chunk_size=300, overlap=50):
    sections = split_sections(text)
    chunks = split_chunks(sections, max_chunk_size, overlap)
    return chunks


def write_chunks_to_file(chunks, pdf_path, namespace=None):
    # Create a 'chunks' directory if it doesn't exist
    if not os.path.exists('chunks'):
        os.makedirs('chunks')

    # Set the output file name using the original PDF filename
    if pdf_path:
        output_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    else:
        output_filename = namespace
    output_file_path = f"./chunks/{output_filename}_chunks.txt"

    # Write the chunks to the output file
    with open(output_file_path, 'w') as f:
        for idx, chunk in enumerate(chunks, start=1):
            f.write(f"Chunk {idx}:\n")
            f.write(chunk)
            f.write("\n\n")"""