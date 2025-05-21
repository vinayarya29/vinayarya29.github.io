import sys
from bs4 import BeautifulSoup

def update_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # 1. Update Blog Post
        post_article = soup.find('article', class_='box post')
        if post_article:
            # Remove all existing content of the article
            for element in post_article.find_all(recursive=False):
                element.decompose()
            # Add the new placeholder paragraph
            placeholder_p = soup.new_tag('p')
            placeholder_p.string = "Information about Vinay Arya's research will be updated here. Please provide the main introduction text."
            post_article.append(placeholder_p)
        else:
            print("Error: Blog post article not found.", file=sys.stderr)
            return False

        # 2. Update Sidebar
        sidebar = soup.find('div', id='sidebar')
        if sidebar:
            excerpts_ul = sidebar.find('ul', class_='divided')
            if excerpts_ul:
                # Remove existing list items
                for li in excerpts_ul.find_all('li', recursive=False):
                    li.decompose()

                publications = [
                    {
                        "date": "September 2023",
                        "title": "Interplay of geometry and shape-engineered-nanoparticles for efficient thermal performance in forced convection-based electronic cooling"
                    },
                    {
                        "date": "July 2023",
                        "title": "Significantly Reduced Thermal Conductivity and Enhanced Thermoelectric Performance of Twisted Bilayer Graphene"
                    },
                    {
                        "date": "May 2023",
                        "title": "Mapping Fluid Structuration to Flow Enhancement in Nanofluidic Channels"
                    }
                ]

                for pub in publications:
                    li = soup.new_tag('li')
                    article = soup.new_tag('article', class_='box excerpt')
                    
                    header = soup.new_tag('header')
                    date_span = soup.new_tag('span', class_='date')
                    date_span.string = pub['date']
                    h3 = soup.new_tag('h3')
                    a_tag = soup.new_tag('a', href="#")
                    a_tag.string = "New Publication" # As per existing structure, title is in <p>
                    h3.append(a_tag)
                    header.append(date_span)
                    header.append(h3)
                    
                    p_tag = soup.new_tag('p')
                    p_tag.string = pub['title']
                    
                    article.append(header)
                    article.append(p_tag)
                    li.append(article)
                    excerpts_ul.append(li)
            else:
                print("Error: Sidebar UL element not found.", file=sys.stderr)
                return False
        else:
            print("Error: Sidebar div not found.", file=sys.stderr)
            return False

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if update_html_file('index.html'):
        print("index.html updated successfully.")
    else:
        print("Failed to update index.html.", file=sys.stderr)
        sys.exit(1)
