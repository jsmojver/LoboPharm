jQuery.fn.hijack = function(afterLoadFunction) {
    var target = this;

    a = target
        .find('a:not(.nohijack)').click(function(event) { // attach click event to all links within (skip nohijack links)
           
           if (event.isDefaultPrevented()) // netko je već preventao default pa nećemo i mi
               return;
           // console.log(this);
  
           $.get(this.href, function(msg) {
             if(msg.substring(0,11)!='javascript:') { // da možemo sa server strane slati javascript po potrebi
               target.html(msg);
               jQuery(target).hijack(afterLoadFunction);
               if (jQuery.isFunction(afterLoadFunction)) afterLoadFunction.call(this);           
               }
             else { eval(msg.substring(11)); return; }
           });   
              
           return false;
        });
     ////////////////////////////////////////////////////////////////////////////////////////
    if(target.find('.method-get').length) {metoda = 'GET';} else metoda = 'POST'; // ako se doda klasa method-get onda šalje get-om 
    b = target.find('form:not(.nohijack)') // hijack all forms within (skip nohijack forms) 
	.each(function(){
		$(this).submit(function(event) { 
				event.preventDefault(); 
				action = $(this).attr('action');
				$(this).find('.ui-autocomplete-input').each(function(index, value){
				    data = $(value).data('autocomplete-value');
				    if(data) $(value).val(data);
				 });
				$.ajax({	
		                   type: metoda, url: action, data: $(this).serialize(),
                		   success: function(msg) { 
                		     if(msg.substring(0,11)!='javascript:') // da možemo sa server strane slati javascript po potrebi
                		         target.html(msg);
                		     else { eval(msg.substring(11)); return; }
                		       
					jQuery(target).hijack(afterLoadFunction);
					}
		    		   });
			});
		
		});
		
		c = target.find('input.autocomplete').each(function(){ // ako input loadanog contenta ima klasu autocomplete, pozovi na njemu funkciju universal_autocomplete
		  universal_autocomplete($(this));
		  // console.log($(this));
		});

     return a, b;


};


