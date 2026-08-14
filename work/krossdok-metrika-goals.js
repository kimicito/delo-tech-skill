// Yandex Metrica Goals for krossdok.ru
// Counter ID: 45030274
// Created: 2026-08-14
//
// Track both: popup open (interest) and form submit (conversion)
// Products: Standard (8800₽), PRO (9800₽), Online, Education

document.addEventListener('DOMContentLoaded', function() {
    
    // Track which popup was last opened
    var lastPopup = null;
    
    // ============================================================
    // STEP 1: Track popup opens (interest / top of funnel)
    // ============================================================
    
    // KROSSDOK Standard (8800 ₽)
    document.querySelectorAll('a[href="#popup:myformstandard"]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            lastPopup = 'standard';
            ym(45030274, 'reachGoal', 'order_standard');
            console.log('[YM] order_standard — popup opened');
        });
    });
    
    // KROSSDOK PRO (9800 ₽)
    document.querySelectorAll('a[href="#popup:myformPRO"]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            lastPopup = 'pro';
            ym(45030274, 'reachGoal', 'order_pro');
            console.log('[YM] order_pro — popup opened');
        });
    });
    
    // KROSSDOK Online (digital version)
    document.querySelectorAll('a[href="#popup:myformONLINE"]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            lastPopup = 'online';
            ym(45030274, 'reachGoal', 'order_online');
            console.log('[YM] order_online — popup opened');
        });
    });
    
    // KROSSDOK Education (B2B — universities/schools)
    document.querySelectorAll('a[href="#popup:myformuniversity"]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            lastPopup = 'education';
            ym(45030274, 'reachGoal', 'order_education');
            console.log('[YM] order_education — popup opened');
        });
    });
    
    // ============================================================
    // STEP 2: Track form submissions (conversion / bottom of funnel)
    // ============================================================
    
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            
            // Route to the right goal based on which popup was opened
            switch(lastPopup) {
                case 'standard':
                    ym(45030274, 'reachGoal', 'form_standard');
                    console.log('[YM] form_standard — form submitted');
                    break;
                    
                case 'pro':
                    ym(45030274, 'reachGoal', 'form_pro');
                    console.log('[YM] form_pro — form submitted');
                    break;
                    
                case 'online':
                    ym(45030274, 'reachGoal', 'form_online');
                    console.log('[YM] form_online — form submitted');
                    break;
                    
                case 'education':
                    ym(45030274, 'reachGoal', 'form_education');
                    console.log('[YM] form_education — form submitted');
                    break;
                    
                default:
                    // Fallback: contact form or other forms not from product popups
                    ym(45030274, 'reachGoal', 'form_contacts');
                    console.log('[YM] form_contacts — general form submitted');
            }
            
            // Reset after submission so next form doesn't inherit
            lastPopup = null;
        });
    });
    
    console.log('[YM] Metrica goals initialized for counter 45030274');
});
