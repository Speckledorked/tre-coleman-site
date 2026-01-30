/**
 * Course Authentication Protection
 * Include this script on any page that requires authentication
 */

const CourseAuth = {
  session: null,
  user: null,

  init() {
    this.session = JSON.parse(localStorage.getItem('session') || 'null');
    this.user = JSON.parse(localStorage.getItem('user') || 'null');
  },

  isLoggedIn() {
    return this.session && this.session.access_token;
  },

  hasCoruseAccess() {
    return this.user && this.user.has_course_access;
  },

  getToken() {
    return this.session?.access_token;
  },

  getUser() {
    return this.user;
  },

  async verifySession() {
    if (!this.isLoggedIn()) {
      return false;
    }

    try {
      const response = await fetch('/.netlify/functions/auth-verify', {
        headers: {
          'Authorization': `Bearer ${this.getToken()}`
        }
      });

      if (!response.ok) {
        this.logout();
        return false;
      }

      const data = await response.json();

      // Update user data
      this.user = data.user;
      localStorage.setItem('user', JSON.stringify(data.user));

      return data.valid;
    } catch (error) {
      console.error('Session verification failed:', error);
      return false;
    }
  },

  logout() {
    localStorage.removeItem('session');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
  },

  // Protect a page - redirects to login if not authenticated
  async protectPage(requireCourseAccess = false) {
    this.init();

    if (!this.isLoggedIn()) {
      window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
      return false;
    }

    const isValid = await this.verifySession();
    if (!isValid) {
      window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
      return false;
    }

    if (requireCourseAccess && !this.user.has_course_access) {
      window.location.href = '/course/no-access.html';
      return false;
    }

    return true;
  },

  // Render user info in a container
  renderUserInfo(containerId) {
    const container = document.getElementById(containerId);
    if (!container || !this.user) return;

    container.innerHTML = `
      <span class="user-name">${this.user.name}</span>
      <button onclick="CourseAuth.logout()" class="logout-btn">Log Out</button>
    `;
  }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  CourseAuth.init();
});
