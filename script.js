/* ============================================================
   АэроТех 74 — интерактив макета
   ============================================================ */
(function () {
  'use strict';

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- header ---------- */
  var header = $('#header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- mobile nav ---------- */
  var burger = $('#burger');
  var nav = $('#nav');

  function closeNav() {
    nav.classList.remove('is-open');
    burger.setAttribute('aria-expanded', 'false');
  }

  burger.addEventListener('click', function () {
    var open = nav.classList.toggle('is-open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  $$('#nav a').forEach(function (a) {
    a.addEventListener('click', closeNav);
  });

  document.addEventListener('click', function (e) {
    if (nav.classList.contains('is-open') && !nav.contains(e.target) && !burger.contains(e.target)) {
      closeNav();
    }
  });

  /* ---------- reveal on scroll ---------- */
  var revealEls = $$('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- animated stats ---------- */
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function animateCount(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    if (reduceMotion) {
      el.textContent = target.toLocaleString('ru-RU');
      return;
    }
    var start = null;
    var dur = 1400;

    function frame(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased).toLocaleString('ru-RU');
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  var counters = $$('[data-count]');
  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          cio.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { cio.observe(c); });
  } else {
    counters.forEach(animateCount);
  }

  /* ---------- portfolio filter ---------- */
  var filters = $$('.filter');
  var cards = $$('.project');

  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cat = btn.getAttribute('data-filter');

      filters.forEach(function (b) {
        b.classList.remove('is-active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('is-active');
      btn.setAttribute('aria-selected', 'true');

      cards.forEach(function (card) {
        var show = cat === 'all' || card.getAttribute('data-cat') === cat;
        card.classList.toggle('is-hidden', !show);
        if (show) {
          card.classList.remove('is-in');
          // re-trigger the reveal animation
          void card.offsetWidth;
          card.classList.add('is-in');
        }
      });
    });
  });

  /* ---------- equipment calculator ---------- */
  var area = $('#area');
  if (area) {
    var areaOut = $('#areaOut');
    var powerOut = $('#powerOut');
    var airOut = $('#airOut');

    var renderCalc = function () {
      var a = parseInt(area.value, 10);
      var kw = a / 10;              // 1 кВт на 10 м²
      var air = a * 3;              // 3 м³/ч на м²

      areaOut.textContent = a.toLocaleString('ru-RU');
      powerOut.textContent = kw.toLocaleString('ru-RU', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' кВт';
      airOut.textContent = Math.round(air).toLocaleString('ru-RU') + ' м³/ч';

      var pct = ((a - 10) / (300 - 10)) * 100;
      area.style.setProperty('--p', pct + '%');
    };

    area.addEventListener('input', renderCalc);
    renderCalc();
  }

  /* ---------- phone mask ---------- */
  function maskPhone(input) {
    input.addEventListener('input', function () {
      var digits = input.value.replace(/\D/g, '');
      if (digits[0] === '8') digits = '7' + digits.slice(1);
      if (digits[0] !== '7') digits = '7' + digits;
      digits = digits.slice(0, 11);

      var out = '+7';
      if (digits.length > 1) out += ' (' + digits.slice(1, 4);
      if (digits.length >= 5) out += ') ' + digits.slice(4, 7);
      if (digits.length >= 8) out += '-' + digits.slice(7, 9);
      if (digits.length >= 10) out += '-' + digits.slice(9, 11);
      input.value = out;
    });

    input.addEventListener('focus', function () {
      if (!input.value) input.value = '+7 (';
    });

    input.addEventListener('blur', function () {
      if (input.value.replace(/\D/g, '').length <= 1) input.value = '';
    });
  }
  $$('input[type="tel"]').forEach(maskPhone);

  /* ---------- lead forms ---------- */
  function setupForm(form) {
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var valid = true;
      $$('input[required], select[required]', form).forEach(function (field) {
        if (field.type === 'checkbox') return;
        var empty = !field.value.trim();
        if (field.type === 'tel') {
          empty = field.value.replace(/\D/g, '').length < 11;
        }
        field.closest('.field').classList.toggle('has-error', empty);
        if (empty) valid = false;
      });

      var agree = $('input[type="checkbox"]', form);
      if (agree && !agree.checked) valid = false;

      if (!valid) {
        var bad = $('.has-error input, .has-error select', form);
        if (bad) bad.focus();
        return;
      }

      var btn = $('button[type="submit"]', form);
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Отправляем…';
      }

      setTimeout(function () {
        form.classList.add('is-sent');
      }, 700);
    });

    $$('input, select, textarea', form).forEach(function (field) {
      field.addEventListener('input', function () {
        var wrap = field.closest('.field');
        if (wrap) wrap.classList.remove('has-error');
      });
    });
  }

  setupForm($('#leadForm'));
  setupForm($('#leadForm2'));

  /* footer mini form */
  var mini = $('#leadForm3');
  if (mini) {
    mini.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = $('input', mini);
      if (input.value.replace(/\D/g, '').length < 11) {
        input.focus();
        input.style.borderColor = '#e2564c';
        return;
      }
      mini.classList.add('is-sent');
    });
  }

  /* ---------- floating call button hides over footer ---------- */
  var footer = document.querySelector('.footer');
  var floatBtn = document.querySelector('.float-call');
  if (footer && floatBtn && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        floatBtn.classList.toggle('is-off', entry.isIntersecting);
      });
    }, { threshold: 0.02 }).observe(footer);
  }

  /* ---------- FAQ: one open at a time ---------- */
  var faqItems = $$('.faq__item');
  faqItems.forEach(function (item) {
    item.addEventListener('toggle', function () {
      if (item.open) {
        faqItems.forEach(function (other) {
          if (other !== item) other.open = false;
        });
      }
    });
  });

  /* ---------- smooth anchor offset ---------- */
  $$('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var id = link.getAttribute('href');
      if (id === '#' || id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;

      e.preventDefault();
      var top = target.getBoundingClientRect().top + window.pageYOffset - 88;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });
})();
