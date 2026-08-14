<script>
// Yandex Metrica Goals for supplychains.ru
// Counter: 30201489

document.addEventListener('DOMContentLoaded', function() {
  // Goal: Form submissions
  document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'form_contact');
    });
  });

  // Goal: Popup open
  document.querySelectorAll('.t708__btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'popup_open');
    });
  });

  // Goals: External links
  document.querySelectorAll('a[href*="krossdok.ru"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'link_krossdok');
    });
  });
  document.querySelectorAll('a[href*="logistoria.com"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'link_logistoria');
    });
  });
  document.querySelectorAll('a[href*="thekadenagame"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'link_kadena');
    });
  });
  document.querySelectorAll('a[href*="thebeergame"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'link_beergame');
    });
  });
  document.querySelectorAll('a[href*="logistoria-platform.vercel.app"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'link_platform');
    });
  });

  // Goals: Social links
  document.querySelectorAll('a[href*="t.me/supplychains"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'social_telegram');
    });
  });
  document.querySelectorAll('a[href*="vk.com/logistoriagames"]').forEach(function(link) {
    link.addEventListener('click', function() {
      if (typeof ym !== 'undefined') ym(30201489, 'reachGoal', 'social_vk');
    });
  });
});
</script>