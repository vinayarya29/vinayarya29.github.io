import sys
import re
from bs4 import BeautifulSoup, NavigableString

def update_copyright_in_file(filepath, current_year=2024):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        copyright_li_tag = None
        
        # Attempt to find the <li> tag containing copyright information
        # Search within common footer landmarks first
        possible_parents = soup.select('div#copyright ul.links, section#footer ul.links, div#copyright, section#footer')
        if not possible_parents: # If no specific landmarks, search the whole body
            possible_parents = [soup.body] if soup.body else []

        for parent in possible_parents:
            if not parent: continue
            lis = parent.find_all('li', recursive=True)
            for li in lis:
                # Check the combined text of the <li>
                li_text = li.get_text(strip=True)
                if "&copy; Vinay Arya" in li_text and "All rights reserved." in li_text:
                    copyright_li_tag = li
                    break
            if copyright_li_tag:
                break
        
        if not copyright_li_tag:
            print(f"Warning: Copyright <li> element not found in {filepath}. No update made.", file=sys.stderr)
            return False

        # Modify the text content of the found <li>
        # This approach replaces the whole content of <li> if it's simple, 
        # or tries to modify text nodes if complex.
        
        # Form the new copyright string
        new_copyright_string = f"&copy; Vinay Arya {current_year}. All rights reserved."

        # Check if the content is already correct
        if new_copyright_string in copyright_li_tag.get_text(strip=True):
            print(f"Info: Copyright year in {filepath} already up-to-date.", file=sys.stdout)
            return True

        # Strategy: Iterate through NavigableString children and replace the one with copyright.
        # If not found, and if the <li> has no other tags, just set its string.
        
        modified_in_navigable_string = False
        for child_node in copyright_li_tag.children:
            if isinstance(child_node, NavigableString):
                original_text = str(child_node)
                # Remove old year if present and not the current year
                text_without_old_year = re.sub(r"(\s*&copy;\s*Vinay\s*Arya\s*)(\d{4})(\.?\s*All\s*rights\s*reserved\.?)", r"\1\3", original_text, flags=re.IGNORECASE)
                # Add new year
                updated_text = re.sub(r"(&copy;\s*Vinay\s*Arya)(\.?\s*All\s*rights\s*reserved\.?)", rf"\1 {current_year}\2", text_without_old_year, flags=re.IGNORECASE)

                if updated_text != original_text:
                    child_node.replace_with(NavigableString(updated_text))
                    modified_in_navigable_string = True
                    break 
        
        if not modified_in_navigable_string:
            # If no direct NavigableString was updated (e.g., complex structure or already correct but caught by string check earlier)
            # Or if the <li> tag has no children but just a string (copyright_li_tag.string)
            # This is a fallback if the above didn't work.
            # For simple <li>text</li>, this is safe.
            # If <li><a>text</a></li>, this would wipe out <a>. The above loop should handle it.
            # Given the specific text, it's likely to be a direct string or within a simple structure.
            
            # Check if it's a simple <li> with just text.
            if not copyright_li_tag.find(True, recursive=False): # No child tags
                 copyright_li_tag.string = new_copyright_string
            else:
                # The structure is more complex, and the direct NavigableString replacement failed.
                # This might happen if the text is split across multiple NavigableStrings or within other tags.
                # For now, we'll indicate that an automatic update for this complex case was not straightforward.
                print(f"Warning: Copyright text in {filepath} found in a complex <li> structure that was not automatically updated by simple text node replacement. Manual check might be needed if not already correct.", file=sys.stderr)
                # To avoid breaking complex structures, we don't force update here unless sure.
                # If the earlier check `new_copyright_string in copyright_li_tag.get_text(strip=True)` passed, it's fine.
                # If not, it means it's not correct AND not simple.
                if not (f"&copy; Vinay Arya {current_year}. All rights reserved." in copyright_li_tag.get_text(strip=True)):
                    return False # Indicate update didn't fully succeed as expected for complex case.


        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred while processing {filepath}: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_copyright_year.py <html_filepath>", file=sys.stderr)
        sys.exit(1)
    
    filepath_to_modify = sys.argv[1]
    if update_copyright_in_file(filepath_to_modify):
        print(f"Copyright year in {filepath_to_modify} processed.")
    else:
        print(f"Failed to update copyright year in {filepath_to_modify}.", file=sys.stderr)
        sys.exit(1)
