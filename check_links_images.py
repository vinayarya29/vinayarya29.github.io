import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

# Construct the list of all known files in the repository.
# This should be comprehensive based on the ls() tool output.
# For simplicity in this environment, I'll use a slightly less exhaustive list
# focusing on common locations. A more robust solution would use the exact ls output.
REPO_FILES = {
    # Root files
    "LICENSE.txt", "README.md", "README.txt", "_config.yml", "academics.html",
    "calculator.html", "contact.html", "cv.html", "favicon.png", "index.html",
    "publications.html", "research.html", "sitemap.xml",
    # Assets
    "assets/css/fontawesome-all.min.css", "assets/css/images/bracket.svg", "assets/css/main.css",
    "assets/js/breakpoints.min.js", "assets/js/browser.min.js", "assets/js/jquery.dropotron.min.js",
    "assets/js/jquery.min.js", "assets/js/main.js", "assets/js/util.js",
    "assets/sass/main.scss", # Assuming sass files are not directly linked but good to list
    "assets/webfonts/fa-brands-400.eot", "assets/webfonts/fa-brands-400.svg", "assets/webfonts/fa-brands-400.ttf", "assets/webfonts/fa-brands-400.woff", "assets/webfonts/fa-brands-400.woff2",
    "assets/webfonts/fa-regular-400.eot", "assets/webfonts/fa-regular-400.svg", "assets/webfonts/fa-regular-400.ttf", "assets/webfonts/fa-regular-400.woff", "assets/webfonts/fa-regular-400.woff2",
    "assets/webfonts/fa-solid-900.eot", "assets/webfonts/fa-solid-900.svg", "assets/webfonts/fa-solid-900.ttf", "assets/webfonts/fa-solid-900.woff", "assets/webfonts/fa-solid-900.woff2",
    # Images
    "images/avatar.jpg", "images/banner.jpg", "images/banner.mp4", "images/headshot.jpg",
    "images/logo.jpg", "images/logo.png", "images/party_sep22.jpg",
    "images/pic01.jpg", "images/pic02.jpg", "images/pic03.jpg", "images/pic04.jpg",
    "images/pic05.jpg", "images/pic06.jpg", "images/pic07.jpg", "images/pic08.jpg",
    "images/pic09.jpg", "images/pic10.jpg", "images/pic11.jpg", "images/pic12.jpg",
    # Research files
    "research/MD.html", "research/PMRF.html", "research/favicon.ico",
    "research/resources.html", "research/upcoming.html",
    # Resume files (example, might not be linked)
    "resume_files/colorschememapping.xml", "resume_files/filelist.xml", "resume_files/image001.png",
    "resume_files/image002.png", "resume_files/image003.png", "resume_files/image004.png",
    "resume_files/image005.png", "resume_files/item0006.xml", "resume_files/props007.xml",
    "resume_files/themedata.thmx",
    # Python scripts (not typically linked, but good for completeness if checking all files)
    "add_nav_link.py", "create_cv_html.py", "update_copyright_year.py",
    "modify_contact_html.py", "modify_html.py", "modify_md_html.py",
    "modify_publications_html.py", "modify_research_html.py",
    "modify_resources_html.py", "modify_upcoming_html.py", "check_links_images.py"
}
# Adding directories themselves is not standard for file existence checks,
# but useful for validating paths that might point to a directory if that's intended.
# For now, REPO_FILES contains files.

def check_html_file_links(filepath, all_repo_files):
    broken_links = []
    suspicious_images = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        base_dir = os.path.dirname(filepath) # Directory of the current HTML file

        # Check <a> tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            original_href = href # For reporting

            # Skip external links, mailto, tel, and empty or anchor-only links
            parsed_href = urlparse(href)
            if parsed_href.scheme or parsed_href.netloc or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('#') or not href:
                continue

            # Normalize path: remove query strings or fragments for file existence check
            href = parsed_href.path
            href = unquote(href) # Handle URL-encoded characters like %20

            # Resolve the path relative to the current file
            if base_dir and base_dir != '.': # If the file is in a subdirectory
                absolute_path = os.path.normpath(os.path.join(base_dir, href))
            else: # File is in the root directory
                absolute_path = os.path.normpath(href)
            
            # Normalize for comparison (e.g. remove leading ./)
            absolute_path = absolute_path.lstrip('./')

            if absolute_path not in all_repo_files:
                # Extra check: if it's a path like "filename.html" from "subdir/another.html",
                # it might resolve to "subdir/filename.html". Check that too.
                # This is already handled by os.path.join if href is not ../
                broken_links.append({"file": filepath, "tag": str(a_tag), "href": original_href, "resolved_path": absolute_path})

        # Check <img> tags
        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src'].strip()
            original_src = src # For reporting

            parsed_src = urlparse(src)
            if parsed_src.scheme or parsed_src.netloc: # Skip external images
                continue
            
            src = parsed_src.path
            src = unquote(src)

            if base_dir and base_dir != '.':
                absolute_path = os.path.normpath(os.path.join(base_dir, src))
            else:
                absolute_path = os.path.normpath(src)
            
            absolute_path = absolute_path.lstrip('./')

            if absolute_path not in all_repo_files:
                suspicious_images.append({"file": filepath, "tag": str(img_tag), "src": original_src, "resolved_path": absolute_path})
                
    except Exception as e:
        print(f"Error processing file {filepath}: {e}", file=sys.stderr)
        
    return broken_links, suspicious_images

if __name__ == '__main__':
    files_to_check = [
        "index.html", "publications.html", "research.html", "contact.html", "cv.html",
        "research/PMRF.html", "research/MD.html", "research/resources.html", "research/upcoming.html"
    ]
    
    all_broken_links = []
    all_suspicious_images = []
    
    print("Starting link and image check...")
    for html_file in files_to_check:
        print(f"Checking {html_file}...")
        broken, suspicious = check_html_file_links(html_file, REPO_FILES)
        all_broken_links.extend(broken)
        all_suspicious_images.extend(suspicious)
        
    print("\n--- Link and Image Check Report ---")
    if all_broken_links:
        print("\nBroken Internal Links Found:")
        for item in all_broken_links:
            print(f"  File: {item['file']}, Link Tag: {item['tag']}, Href: \"{item['href']}\", Resolved Path: \"{item['resolved_path']}\" (Not Found)")
    else:
        print("\nNo broken internal links found.")
        
    if all_suspicious_images:
        print("\nSuspicious Image Paths Found:")
        for item in all_suspicious_images:
            print(f"  File: {item['file']}, Image Tag: {item['tag']}, Src: \"{item['src']}\", Resolved Path: \"{item['resolved_path']}\" (Not Found)")
    else:
        print("\nNo suspicious image paths found.")
    
    print("\n--- End of Report ---")
