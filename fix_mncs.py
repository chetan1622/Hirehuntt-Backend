import re

def fix():
    with open('frontend/src/mncs.js', 'r', encoding='utf-8') as f:
        content = f.read()

    def replacer(match):
        prefix = match.group(1)
        hash_part = match.group(2)
        filename = match.group(3)
        return f'{prefix}thumb/{hash_part}{filename}/512px-{filename}.png'

    pattern = r'(https://upload\.wikimedia\.org/wikipedia/(?:commons|en)/)([^/]+/[^/]+/)([^\"\']+?\.svg)'
    new_content = re.sub(pattern, replacer, content)

    with open('frontend/src/mncs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    fix()
