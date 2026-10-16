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

  /**
   * Does the signed-in account hold a course?
   *
   * Called with no argument it answers for the original course, which is what
   * every existing caller meant by "has course access". Called with a slug it
   * answers for that course.
   *
   * `courses` is the authoritative field; `has_course_access` is read as a
   * fallback so a session stored in localStorage BEFORE this shipped still
   * works. Without that fallback, every student signed in at deploy time would
   * be bounced to no-access.html until their next login.
   */
  hasCourseAccess(slug = 'catering-profit') {
    if (!this.user) return false;
    if (Array.isArray(this.user.courses)) return this.user.courses.includes(slug);
    return slug === 'catering-profit' && Boolean(this.user.has_course_access);
  },

  /** Every course slug this account holds. */
  getCourses() {
    if (!this.user) return [];
    if (Array.isArray(this.user.courses)) return this.user.courses;
    return this.user.has_course_access ? ['catering-profit'] : [];
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

  /**
   * Protect a page - redirects to login if not authenticated.
   *
   * `requireCourseAccess` accepts a course slug as well as true/false. true
   * still means the original course, so no existing call site changes
   * meaning; a page in a second course passes its own slug.
   */
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

    if (requireCourseAccess) {
      const slug = typeof requireCourseAccess === 'string'
        ? requireCourseAccess
        : 'catering-profit';
      if (!this.hasCourseAccess(slug)) {
        window.location.href = `/course/no-access.html?course=${encodeURIComponent(slug)}`;
        return false;
      }
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
