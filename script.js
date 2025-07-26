// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        const targetPosition = target.offsetTop - navbarHeight;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
});

// Mobile scroll animations for all sections
function animateOnScroll() {
  // Only run on mobile devices
  if (window.innerWidth > 767) return;
  
  const triggerBottom = window.innerHeight * 0.8; // Trigger when 80% of viewport height is reached
  
  // Service cards animation
  const serviceCards = document.querySelectorAll('.service-card');
  serviceCards.forEach(card => {
    const cardTop = card.getBoundingClientRect().top;
    if (cardTop < triggerBottom) {
      card.classList.add('animate');
    }
  });
  
  // About section animation
  const aboutContent = document.querySelector('.about-content');
  const aboutImage = document.querySelector('.about-image');
  if (aboutContent && aboutImage) {
    const aboutTop = aboutContent.getBoundingClientRect().top;
    if (aboutTop < triggerBottom) {
      aboutContent.classList.add('animate');
      aboutImage.classList.add('animate');
    }
  }
  
  // Gallery animation
  const galleryItems = document.querySelectorAll('.gallery-item');
  galleryItems.forEach(item => {
    const itemTop = item.getBoundingClientRect().top;
    if (itemTop < triggerBottom) {
      item.classList.add('animate');
    }
  });
  
  // Contact section animation
  const contactCard = document.querySelector('.contact-card');
  const contactInfo = document.querySelectorAll('.contact-info');
  
  if (contactCard) {
    const contactTop = contactCard.getBoundingClientRect().top;
    if (contactTop < triggerBottom) {
      contactCard.classList.add('animate');
    }
  }
  
  contactInfo.forEach(info => {
    const infoTop = info.getBoundingClientRect().top;
    if (infoTop < triggerBottom) {
      info.classList.add('animate');
    }
  });
}

// Optimized scroll event handling with throttling
let ticking = false;

function requestTick() {
  if (!ticking) {
    requestAnimationFrame(animateOnScroll);
    ticking = true;
  }
}

function handleScroll() {
  ticking = false;
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Run on scroll and on page load
  window.addEventListener('scroll', requestTick, { passive: true });
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('load', animateOnScroll);
  window.addEventListener('resize', animateOnScroll, { passive: true });
  
  // Initial animation check
  animateOnScroll();
});

// Floating call button analytics (optional)
document.addEventListener('DOMContentLoaded', function() {
  const floatingCallBtn = document.querySelector('.floating-call-btn');
  if (floatingCallBtn) {
    floatingCallBtn.addEventListener('click', function() {
      // Track call button clicks (you can add analytics here)
      console.log('Floating call button clicked');
    });
  }
}); 