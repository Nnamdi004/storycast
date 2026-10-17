/* StoryCast: progressive enhancement for story pages.
 *
 * Everything on the site works without JavaScript (native controls, captions
 * track, full transcript). This script adds:
 *   1. Clickable transcript timestamps that seek the media
 *   2. The currently spoken line highlighted (aria-current) in the transcript
 *   3. A visible live caption line for audio stories
 *   4. A playback speed control and an optional "follow along" scroll
 */
(function () {
  'use strict';

  var media = document.querySelector('.player audio, .player video');
  var body = document.querySelector('.transcript__body');
  var cueEls = Array.prototype.slice.call(document.querySelectorAll('.transcript__cue'));
  if (!media || !body || !cueEls.length) return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cues = cueEls.map(function (el) {
    return {
      el: el,
      start: parseFloat(el.getAttribute('data-start')),
      text: (el.querySelector('.transcript__text') || el).textContent.trim()
    };
  });

  // 1. Turn static <time> stamps into buttons that seek the media.
  cues.forEach(function (cue) {
    var stamp = cue.el.querySelector('time.transcript__time');
    if (!stamp) return;
    var label = stamp.textContent.trim();
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'transcript__time';
    btn.textContent = label;
    btn.setAttribute('aria-label', 'Play from ' + label);
    btn.addEventListener('click', function () {
      media.currentTime = cue.start;
      var played = media.play();
      if (played && played.catch) played.catch(function () { /* autoplay blocked: user can press play */ });
    });
    stamp.replaceWith(btn);
  });

  // Reveal the enhancement-only controls.
  var controls = document.querySelector('[data-enhance]');
  if (controls) controls.hidden = false;

  // 2 + 3. Highlight the active line and mirror it as a live caption.
  var live = document.querySelector('[data-live-captions]');
  var idleCaption = 'Captions will appear here while the story plays.';
  if (live) { live.hidden = false; live.textContent = idleCaption; }
  var follow = document.getElementById('follow-transcript');
  var activeIndex = -1;

  function indexAt(time) {
    var found = -1;
    for (var i = 0; i < cues.length; i++) {
      if (time + 0.05 >= cues[i].start) found = i; else break;
    }
    return found;
  }

  function setActive(index) {
    if (index === activeIndex) return;
    if (activeIndex > -1) cues[activeIndex].el.removeAttribute('aria-current');
    activeIndex = index;
    if (index > -1) {
      cues[index].el.setAttribute('aria-current', 'true');
      if (follow && follow.checked) {
        var top = cues[index].el.offsetTop - body.clientHeight / 3;
        body.scrollTo({ top: Math.max(0, top), behavior: reduceMotion ? 'auto' : 'smooth' });
      }
    }
    if (live) live.textContent = index > -1 ? cues[index].text : idleCaption;
  }

  function sync() { setActive(indexAt(media.currentTime)); }

  media.addEventListener('timeupdate', sync);
  media.addEventListener('seeked', sync);
  media.addEventListener('ended', function () { setActive(-1); });

  // 4. Playback speed.
  var speed = document.getElementById('playback-speed');
  if (speed) {
    speed.addEventListener('change', function () {
      media.playbackRate = parseFloat(speed.value);
    });
  }
})();
