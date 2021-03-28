jQuery(document).ready(function(){

 // Message
  $('.message-wrapper .close').click(function(event) {
    var message = $(this).parent();
    message.slideUp('slow');
    // event.preventDefault();
  });

	$('#login-form').submit(function(){
	
		var action = $(this).attr('action');
		var remember = ($('#remember').is(':checked')) ? 'on' : 'off';
    
		$("#login-message").slideUp(750,function() {
		  $('#login-message').hide();

  		$.post(action, { 
  			username: $('#username').val(),
        passw: $('#passw').val(),
        remember: remember
  		},
  			function(data){
  				if(data.match('success') != null) {
              $('#login-message').hide();
              window.location.href = 'index.htm';    				
          } else {
              $('#login-message').removeClass('ok').removeClass('warning').removeClass('attention').addClass('error');
              $('#login-message p.message-text').html(data);
      				$('#login-message').slideDown('slow');
          }
  			}
  		);
		
		});
		
		return false; 
	
	});

});