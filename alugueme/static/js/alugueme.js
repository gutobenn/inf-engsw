$( document ).ready(function() {
  $('.items-list').masonry({
    itemSelector: '.item'
  });

  $(".likert-field").rating();
});
