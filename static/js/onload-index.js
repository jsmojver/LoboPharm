$(document).ready(function(){

  $("#mainTabs").tabs({
        load: function(event, ui) {
	    $(ui.panel).hijack(); // jQuery hijack plugin, otvara linkove i forme u istom tabu!
        }
    });

   // calendar
  //$("#calendar").jdigiclock();

  // side menu code
  $('#side-menu ul').hide();
  $('#side-menu li a.submenu-link').addClass('bg-close');

  $('#side-menu li a.open').removeClass('bg-close').addClass('bg-open').next().slideDown('slow');

  $('#side-menu li a.submenu-link:not(.no-submenu)').click(function() {

    var submenu         = $(this).next();
    var submenu_link    = $(this);
    var submenu_visible = submenu.is(':visible');

    // close all submenus and set up classes to - close
    $('#side-menu ul').slideUp('normal');
    $('#side-menu > li a.submenu-link').removeClass('bg-open').addClass('bg-close');

    // close submenu - nothing is happening - all submenus are already closed by previous code
    if((submenu.is('ul')) && submenu_visible) {
    }

    // open submenu and set up classes
    if((submenu.is('ul')) && (!submenu_visible)) {
        submenu.slideDown('slow');
        submenu_link.removeClass('bg-close').addClass('bg-open');
    }
    
    return false;
  });

	$('#side-menu li a.no-submenu').click(function () {
			window.location.href = $(this).attr('href'); 
			return false;
	}); 

   $('.submenu-linkovi li a').click(function(event) {
			event.preventDefault();
			load_and_focus_tab($(this).attr('href'), parseInt($(this).attr('tab')));
			return false;
	}); 


  // Messages
  $('.message-wrapper .close').click(function(event) {
    var message = $(this).parent();
    message.slideUp('slow');
    event.preventDefault();
  });

  $('.data-table tbody tr').addClass('odd');
  $('.data-table tbody tr td:first-child').addClass('select');

});
