
import json
import os
from bs4 import BeautifulSoup

def update_blog_html(blog_posts_data, blog_html_path):
    with open(blog_html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    blog_grid = soup.find('div', class_='blog-grid')
    if blog_grid:
        blog_grid.clear() # Clear existing content
        for post in blog_posts_data:
            # Relative path from the site root
            relative_path = os.path.join('blog', post['file_name'])
            
            article_tag = soup.new_tag('article', class_='blog-post')
            
            # Placeholder for post meta, can be expanded if date/category info is available
            post_meta = soup.new_tag('div', class_='post-meta')
            post_meta.string = 'Operations • 7 min read' # Generic placeholder
            article_tag.append(post_meta)

            h3_tag = soup.new_tag('h3')
            a_tag = soup.new_tag('a', href=relative_path)
            a_tag.string = post['title']
            h3_tag.append(a_tag)
            article_tag.append(h3_tag)

            p_tag = soup.new_tag('p')
            # Use a truncated description for the excerpt
            excerpt = post['description']
            if len(excerpt) > 150:
                excerpt = excerpt[:150] + '...'
            p_tag.string = excerpt
            article_tag.append(p_tag)

            read_more_a_tag = soup.new_tag('a', href=relative_path, class_='read-more')
            read_more_a_tag.string = 'Read more →'
            article_tag.append(read_more_a_tag)

            blog_grid.append(article_tag)
    
    with open(blog_html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Updated {blog_html_path} with {len(blog_posts_data)} blog posts.")

def fix_footer_across_all_pages(site_root_dir):
    for root, _, files in os.walk(site_root_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                footer_tag = soup.find('footer')
                if not footer_tag:
                    print(f"No footer tag found in {file_path}, skipping footer update.")
                    continue

                quick_links_ul = None
                # Find the heading (h3 or h4) for 'Quick Links' within the footer
                quick_links_heading = footer_tag.find(['h3', 'h4'], string='Quick Links')
                
                if quick_links_heading:
                    # Find the ul element that is a sibling or child of the parent of the heading
                    # This covers cases where ul is directly after the heading or nested within a div sibling
                    quick_links_ul = quick_links_heading.find_next_sibling('ul')
                    if not quick_links_ul:
                        # If not a direct sibling, check within the parent's children
                        parent_div = quick_links_heading.find_parent(['div'])
                        if parent_div:
                            quick_links_ul = parent_div.find('ul')
                
                if quick_links_ul:
                    # Check if 'Blog' link already exists to avoid duplicates
                    if not quick_links_ul.find('a', href='blog.html'):
                        new_li = soup.new_tag('li')
                        new_a = soup.new_tag('a', href='blog.html')
                        new_a.string = 'Blog'
                        new_li.append(new_a)
                        quick_links_ul.append(new_li)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"Added 'Blog' link to footer in {file_path}")
                    else:
                        print(f"'Blog' link already exists in footer of {file_path}, skipping.")
                else:
                    print(f"Quick Links section (heading or ul) not found in {file_path}, skipping footer update.")

def fix_header_across_all_pages(site_root_dir):
    for root, _, files in os.walk(site_root_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find the Insights dropdown menu in the header
                insights_dropdown_menu = None
                nav_dropdowns = soup.find_all('li', class_='nav-dropdown')
                for dropdown in nav_dropdowns:
                    # Check for 'Insights' link in the dropdown
                    if dropdown.find('a', string='Insights'):
                        insights_dropdown_menu = dropdown.find('div', class_='dropdown-menu')
                        break
                
                if insights_dropdown_menu:
                    # Check if 'Blog' link already exists to avoid duplicates
                    if not insights_dropdown_menu.find('a', href='blog.html'):
                        new_a = soup.new_tag('a', href='blog.html')
                        new_a.string = 'Blog'
                        # Insert 'Blog' link after 'Course Login' if it exists, otherwise append
                        course_login_link = insights_dropdown_menu.find('a', href='login.html')
                        if course_login_link:
                            course_login_link.insert_after(new_a)
                        else:
                            insights_dropdown_menu.append(new_a)
                            
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"Added 'Blog' link to header in {file_path}")
                    else:
                        print(f"'Blog' link already exists in header of {file_path}, skipping.")
                else:
                    print(f"Insights dropdown not found in {file_path}, skipping header update.")

if __name__ == "__main__":
    site_root = "tre-coleman-site"
    blog_data_path = os.path.join(site_root, "blog", "blog_posts_data.json")
    blog_html_path = os.path.join(site_root, "blog.html")

    # Load blog posts data
    with open(blog_data_path, 'r', encoding='utf-8') as f:
        blog_posts = json.load(f)

    # Update blog.html
    update_blog_html(blog_posts, blog_html_path)

    # Fix footer across all pages
    fix_footer_across_all_pages(site_root)

    # Fix header across all pages (specifically the Insights dropdown)
    fix_header_across_all_pages(site_root)

    print("Site update complete.")
