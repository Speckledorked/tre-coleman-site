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

  /**
   * Is the stored access token past its stated expiry?
   *
   * `expires_at` has been stored since auth-login shipped and was never read.
   * Treated as expired 60 seconds early so a token cannot die between this
   * check and the request it was checked for.
   *
   * An absent expires_at is NOT treated as expired: sessions stored before
   * this shipped may not carry one, and calling those expired would sign
   * every one of those students out at once.
   */
  isExpired() {
    const at = this.session && this.session.expires_at;
    if (!at) return false;
    return Date.now() >= (at * 1000) - 60000;
  },

  /**
   * Trade the refresh token for a live session.
   *
   * Returns true only if a new access token was actually stored, so every
   * caller can fall back to its previous behaviour on false. Nothing here
   * clears the session on failure: a network blip should not sign a student
   * out of a course they are part way through.
   */
  async refresh() {
    const refreshToken = this.session && this.session.refresh_token;
    if (!refreshToken) return false;
    try {
      const response = await fetch('/.netlify/functions/auth-refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      if (!response.ok) return false;
      const data = await response.json();
      if (!data || !data.session || !data.session.access_token) return false;
      this.session = data.session;
      localStorage.setItem('session', JSON.stringify(data.session));
      if (data.user) {
        this.user = data.user;
        localStorage.setItem('user', JSON.stringify(data.user));
      }
      return true;
    } catch (error) {
      console.error('Session refresh failed:', error);
      return false;
    }
  },

  getUser() {
    return this.user;
  },

  async verifySession() {
    if (!this.isLoggedIn()) {
      return false;
    }

    // A token past its expiry is renewed before it is used, so the common
    // case never costs a failed request.
    if (this.isExpired()) await this.refresh();

    try {
      let response = await fetch('/.netlify/functions/auth-verify', {
        headers: {
          'Authorization': `Bearer ${this.getToken()}`
        }
      });

      // 401 means the token is dead. Try once to renew it before signing the
      // student out: before this, an expired token logged them straight out,
      // which is what sent people back to the login page mid-course.
      if (response.status === 401 && await this.refresh()) {
        response = await fetch('/.netlify/functions/auth-verify', {
          headers: {
            'Authorization': `Bearer ${this.getToken()}`
          }
        });
      }

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

  /**
   * Forget the stored session WITHOUT navigating.
   *
   * Needed separately from logout() because a caller that is about to send
   * the student somewhere specific has to clear first: login.html honours
   * ?redirect=, so leaving a dead session in storage makes it bounce the
   * student straight back to the page they came from, without ever asking
   * for credentials -- a loop between the two pages.
   */
  clearSession() {
    this.session = null;
    this.user = null;
    try {
      localStorage.removeItem('session');
      localStorage.removeItem('user');
    } catch (_) { /* storage can be unavailable; nothing to clear then */ }
  },

  logout() {
    this.clearSession();
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
