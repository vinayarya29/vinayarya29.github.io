import sys
from bs4 import BeautifulSoup

def update_md_html_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # --- Update "About Molecular Dynamics" section ---
        h2_about_md = soup.find('h2', string='About Molecular Dynamics')
        if h2_about_md:
            # Assuming the paragraph to update is the direct next sibling <p>
            p_about_md = h2_about_md.find_next_sibling('p')
            if p_about_md:
                p_about_md.string = "[Placeholder for user to provide basic details of MD software, e.g., GROMACS, LAMMPS, etc., and their applications in your research.]"
            else:
                print(f"Warning: No <p> tag found immediately after 'About Molecular Dynamics' <h2> in {filepath}", file=sys.stderr)
                # Optionally create the <p> if it's missing, though the task implies it exists
        else:
            print(f"Error: <h2>About Molecular Dynamics</h2> not found in {filepath}", file=sys.stderr)
            # If this critical section is missing, we might not want to proceed or should handle it
            # For now, we'll continue to the next section if this one fails

        # --- Update "Problems Resolved" section ---
        h2_problems_resolved = soup.find('h2', string='Problems Resolved')
        if h2_problems_resolved:
            # Assuming the paragraph to update is the direct next sibling <p>
            p_problems_resolved = h2_problems_resolved.find_next_sibling('p')
            if p_problems_resolved:
                p_problems_resolved.string = "[Placeholder for user to describe specific research problems addressed using molecular dynamics, including key findings and links to relevant publications if any.]"
            else:
                print(f"Warning: No <p> tag found immediately after 'Problems Resolved' <h2> in {filepath}", file=sys.stderr)
        else:
            print(f"Error: <h2>Problems Resolved</h2> not found in {filepath}", file=sys.stderr)

        # Check if any modifications were attempted
        if not h2_about_md and not h2_problems_resolved:
            print(f"Error: Neither target section found in {filepath}. No changes made.", file=sys.stderr)
            return False # Indicate failure if no relevant sections were found

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    except Exception as e:
        print(f"An error occurred in update_md_html_file: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if update_md_html_file('research/MD.html'):
        print("research/MD.html updated successfully.")
    else:
        print("Failed to update research/MD.html.", file=sys.stderr)
        sys.exit(1)
