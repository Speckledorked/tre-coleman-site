
import markdown
import os
import json

def get_html_template(title, description, content):
    # This template is based on the structure observed in index.html and menu-engineering.html
    # It includes the header, footer, and basic styling links.
    # The content will be injected into the main section.
    template = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <title>{title} | Tre Coleman</title>
    <meta name="description" content="{description}" />
    <link rel="stylesheet" href="style.css" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
      /* Basic blog post styling to match the site\'s aesthetic */
      .blog-post-container {{
        max-width: 800px;
        margin: 4rem auto;
        padding: 0 2rem;
      }}
      .blog-post-container h1 {{
        font-size: 2.8rem;
        color: var(--primary-navy);
        margin-bottom: 1.5rem;
        line-height: 1.2;
      }}
      .blog-post-container h2 {{
        font-size: 2rem;
        color: var(--primary-navy);
        margin-top: 2rem;
        margin-bottom: 1rem;
      }}
      .blog-post-container h3 {{
        font-size: 1.5rem;
        color: var(--primary-navy);
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
      }}
      .blog-post-container p {{
        margin-bottom: 1rem;
        line-height: 1.7;
        color: var(--text-dark);
      }}
      .blog-post-container ul,
      .blog-post-container ol {{
        margin-bottom: 1rem;
        padding-left: 1.5rem;
      }}
      .blog-post-container li {{
        margin-bottom: 0.5rem;
        line-height: 1.6;
      }}
      .blog-post-container img {{
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1.5rem 0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      }}
      .blog-post-container strong {{
        font-weight: 600;
      }}
      .blog-post-container em {{
        font-style: italic;
      }}
      .blog-post-container a {{
        color: var(--accent-gold);
        text-decoration: underline;
      }}
      .blog-post-container a:hover {{
        text-decoration: none;
      }}
      .blog-post-meta {{
        font-size: 0.9rem;
        color: var(--text-medium);
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--bg-cream);
        padding-bottom: 1rem;
      }}
    </style>
  </head>
  <body>
    <!-- Mobile Menu Overlay -->
    <div class="mobile-overlay" id="mobileOverlay"></div>

    <!-- Header -->
    <header>
      <div class="container">
        <div class="logo"><a href="index.html" style="color: white; text-decoration: none;">Tre Coleman</a></div>
        <button class="mobile-menu-toggle" id="mobileMenuToggle" aria-label="Toggle navigation menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
        <nav id="mainNav">
          <ul>
              <li><a href="profit-leak-snapshot.html" class="nav-cta">Snapshot</a></li>
              <li><a href="services.html">Services</a></li>
              <li><a href="advisory.html">Advisory</a></li>
              <li class="nav-dropdown">
                  <a href="#" onclick="return false;">Insights</a>
                  <div class="dropdown-menu">
                      <a href="catering-profit.html">Catering Profit System</a>
                      <a href="login.html">Course Login</a>
                      <a href="blog.html">Blog</a>
                  </div>
              </li>
              <li class="nav-dropdown">
                  <a href="#" onclick="return false;">Resources</a>
                  <div class="dropdown-menu">
                      <a href="audit.html">Restaurant Ops Audit</a>
                      <a href="food-truck-audit.html">Food Truck Launch Audit</a>
                      <a href="playbook.html">90-Day Profit Playbook</a>
                  </div>
              </li>
              <li><a href="about.html">About</a></li>
              <li><a href="contact.html">Contact</a></li>
          </ul>
        </nav>
      </div>
    </header>

    <main>
      <div class="container blog-post-container">
        {content}
      </div>
    </main>

    <footer>
      <div class="container">
        <div class="footer-grid">
          <div class="footer-col company-info">
            <h3>Tre Coleman</h3>
            <p>Restaurant Operations Consultant</p>
            <p>Solving complex operational challenges for independent restaurants and multi-unit brands.</p>
            <div class="social-links">
              <a href="https://www.linkedin.com/in/trecoleman/" target="_blank" aria-label="LinkedIn"><i class="fab fa-linkedin"></i></a>
              <a href="https://www.facebook.com/trecolemanconsulting" target="_blank" aria-label="Facebook"><i class="fab fa-facebook"></i></a>
              <a href="https://www.instagram.com/trecolemanconsulting/" target="_blank" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
            </div>
          </div>
          <div class="footer-col quick-links">
            <h3>Quick Links</h3>
            <ul>
              <li><a href="services.html">Services</a></li>
              <li><a href="advisory.html">Advisory</a></li>
              <li><a href="about.html">About</a></li>
              <li><a href="contact.html">Contact</a></li>
              <li><a href="blog.html">Blog</a></li>
            </ul>
          </div>
          <div class="footer-col resources">
            <h3>Resources</h3>
            <ul>
              <li><a href="audit.html">Restaurant Ops Audit</a></li>
              <li><a href="food-truck-audit.html">Food Truck Launch Audit</a></li>
              <li><a href="playbook.html">90-Day Profit Playbook</a></li>
              <li><a href="catering-profit.html">Catering Profit System</a></li>
            </ul>
          </div>
          <div class="footer-col newsletter">
            <h3>Stay Connected</h3>
            <p>Get insights and strategies delivered to your inbox.</p>
            <form action="https://formspree.io/f/xeqyvjqw" method="POST" class="newsletter-form">
              <input type="email" name="email" placeholder="Your email address" required>
              <button type="submit" class="button">Subscribe</button>
            </form>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2024 Tre Coleman. All rights reserved. <a href="privacy.html">Privacy Policy</a></p>
        </div>
      </div>
    </footer>

    <script src="header-scroll.js"></script>
    <script src="exit-intent-popup.js"></script>
    <script src="analytics.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", function() {{
        const mobileMenuToggle = document.getElementById("mobileMenuToggle");
        const mainNav = document.getElementById("mainNav");
        const mobileOverlay = document.getElementById("mobileOverlay");
        const navDropdowns = document.querySelectorAll(".nav-dropdown > a");

        mobileMenuToggle.addEventListener("click", function() {{
          mainNav.classList.toggle("active");
          mobileOverlay.style.display = mainNav.classList.contains("active") ? "block" : "none";
          mobileMenuToggle.classList.toggle("active");
        }});

        mobileOverlay.addEventListener("click", function() {{
          mainNav.classList.remove("active");
          mobileOverlay.style.display = "none";
          mobileMenuToggle.classList.remove("active");
        }});

        navDropdowns.forEach(dropdownToggle => {{
          dropdownToggle.addEventListener("click", function(e) {{
            if (window.innerWidth <= 1024) {{ // Only for mobile/tablet
              e.preventDefault();
              const parentLi = this.closest(".nav-dropdown");
              parentLi.classList.toggle("active");
            }}
          }});
        }});
      }});
    </script>
  </body>
</html>
'''
    return template.format(title=title, description=description, content=content)

def convert_md_to_html(md_file_path, output_dir):
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Extract title and a short description from the Markdown content
    # Assuming the first line is the title (H1) and the next paragraph is the description
    lines = md_content.split('\n')
    title = "Untitled Blog Post"
    description = "A blog post from Tre Coleman."

    if lines and lines[0].strip().startswith('# '):
        title = lines[0].strip('# ').strip()
        # Try to find a description in the next few lines
        for i in range(1, min(len(lines), 5)): # Check up to 5 lines for a description
            if lines[i].strip() and not lines[i].strip().startswith('#'):
                description = lines[i].strip()
                break

    html_content = markdown.markdown(md_content)

    full_html = get_html_template(title, description, html_content)

    # Create a clean filename for the HTML file
    base_name = os.path.basename(md_file_path)
    html_file_name = base_name.replace('.md', '.html').replace(' ', '-').lower()
    output_path = os.path.join(output_dir, html_file_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    return {
        'title': title,
        'description': description,
        'file_name': html_file_name,
        'output_path': output_path
    }

if __name__ == "__main__":
    site_root = "tre-coleman-site"
    input_files = [
        "/home/ubuntu/upload/blog_post_1_profit_leaks_rewritten.md",
        "/home/ubuntu/upload/blog_post_2_systems_growth_rewritten.md",
        "/home/ubuntu/upload/blog_post_3_menu_engineering_rewritten.md",
        "/home/ubuntu/upload/blog_post_4_fractional_coo_rewritten.md",
        "/home/ubuntu/upload/blog_post_5_catering_profitability_rewritten.md"
    ]
    output_directory = os.path.join(site_root, "blog")
    os.makedirs(output_directory, exist_ok=True)

    blog_posts_data = []
    for md_file in input_files:
        post_data = convert_md_to_html(md_file, output_directory)
        blog_posts_data.append(post_data)
    
    # Save blog posts data to a JSON file for later use
    with open(os.path.join(output_directory, 'blog_posts_data.json'), 'w') as f:
        json.dump(blog_posts_data, f, indent=4)

    print(f"Converted {len(blog_posts_data)} markdown files to HTML in {output_directory}")
    for post in blog_posts_data:
        print(f"  - {post['title']} -> {post['output_path']}")
