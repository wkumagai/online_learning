/**
 * NexaScience - main.js
 * Handles: header scroll state, mobile nav, active nav link,
 *          scroll-triggered reveal animations.
 */

(function () {
  'use strict';

  /* ── DOM refs ── */
  const header    = document.getElementById('site-header');
  const navToggle = document.getElementById('nav-toggle');
  const siteNav   = document.getElementById('site-nav');
  const navLinks  = siteNav ? siteNav.querySelectorAll('a') : [];

  /* ============================================================
     1. Header: add .scrolled class after scrolling past 80px
     ============================================================ */
  function onScroll() {
    if (window.scrollY > 80) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    updateActiveNav();
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // run once on load

  /* ============================================================
     2. Mobile nav toggle
     ============================================================ */
  if (navToggle && siteNav) {
    navToggle.addEventListener('click', function () {
      const isOpen = siteNav.classList.toggle('open');
      navToggle.classList.toggle('open', isOpen);
      navToggle.setAttribute('aria-expanded', String(isOpen));
      navToggle.setAttribute('aria-label', isOpen ? 'メニューを閉じる' : 'メニューを開く');
      // Prevent body scroll when nav is open
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close nav when a link is clicked
    navLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        siteNav.classList.remove('open');
        navToggle.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'メニューを開く');
        document.body.style.overflow = '';
      });
    });

    // Close nav on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && siteNav.classList.contains('open')) {
        siteNav.classList.remove('open');
        navToggle.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        navToggle.focus();
      }
    });
  }

  /* ============================================================
     3. Active nav link highlighting based on scroll position
     ============================================================ */
  const sections = document.querySelectorAll('section[id], div[id="top"]');

  function updateActiveNav() {
    let current = '';
    const scrollY = window.scrollY;

    sections.forEach(function (section) {
      const sectionTop    = section.offsetTop - 120;
      const sectionBottom = sectionTop + section.offsetHeight;
      if (scrollY >= sectionTop && scrollY < sectionBottom) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(function (link) {
      const href = link.getAttribute('href');
      if (href === '#' + current) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  /* ============================================================
     4. Scroll-triggered reveal animations (IntersectionObserver)
     ============================================================ */
  function initReveal() {
    // Add .reveal class to elements that should animate in
    const revealTargets = [
      '.about-text',
      '.about-visual',
      '.service-card',
      '.news-item',
      '.contact-lead',
      '.contact-cta',
      '.mission-block',
    ];

    revealTargets.forEach(function (selector, selectorIndex) {
      document.querySelectorAll(selector).forEach(function (el, i) {
        el.classList.add('reveal');
        // Stagger items within the same selector group
        if (i < 4) {
          el.classList.add('reveal-delay-' + (i % 3 + 1));
        }
      });
    });

    if (!('IntersectionObserver' in window)) {
      // Fallback: show everything immediately
      document.querySelectorAll('.reveal').forEach(function (el) {
        el.classList.add('visible');
      });
      return;
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px',
      }
    );

    document.querySelectorAll('.reveal').forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ============================================================
     5. Smooth scroll for anchor links (polyfill for older Safari)
     ============================================================ */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
      anchor.addEventListener('click', function (e) {
        const targetId = this.getAttribute('href').slice(1);
        if (!targetId) return;
        const target = document.getElementById(targetId);
        if (!target) return;
        e.preventDefault();
        const headerHeight = header ? header.offsetHeight : 0;
        const top = target.getBoundingClientRect().top + window.scrollY - headerHeight;
        window.scrollTo({ top: top, behavior: 'smooth' });
      });
    });
  }

  /* ============================================================
     6. Init on DOM ready
     ============================================================ */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initReveal();
      initSmoothScroll();
    });
  } else {
    initReveal();
    initSmoothScroll();
  }

})();
