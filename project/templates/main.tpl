<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>Diocles</title>

        <script src="/static/js/jquery-1.6.4.min.js" type="text/javascript"></script> 
        <script type="text/javascript" charset="utf-8">
                $(document).ready(function() {
                });

	String.prototype.isEan13 = function(){ if (isNaN(this)) return false; s=(this.slice(0,-1)); c=(s+0).split('').reverse(); n=0; for(var i in c){n+=(i%2)?c[i]*3:+c[i]}; return this==(s+((10-(n%10))%10)) }
	String.prototype.isUPC12 = function() { if (isNaN(this) || this.length != 12) return false; return (0+this).isEan13(); }

	// Keypress handleri za citac

	keycode = ''; kbtimestamp = new Date().getTime();

	$(document).keypress(function(e)
	{
		if ((e.which > 47 && e.which < 58) || e.which == 13) { // stisnut je broj ili enter
			now = new Date().getTime(); 
			if((now-kbtimestamp)<100) { 
				if(e.which == 13) { code_submit(keycode); keycode=''; } else keycode += String.fromCharCode(e.keyCode); 
				kbtimestamp = now; return false;
				}
			else { keycode='' + String.fromCharCode(e.keyCode); kbtimestamp = now;  }
		}
		if(e.which in {70:0, 102:0}) { if($('#inq').is(':focus')) {return true;} else {$('#inq').val('').focus(); return false;} } // Ako je stisnuto f ili F a forma NEMA fokus, postavi fokus.
	});

	function code_submit(code) {
		$.get('ajax/' + code, function(data) {
			  $('#div').html(data);
			  alert('Load was performed.');
		});
	
	}


        </script>

</head>
<body>
    <div id="container" class="flip">
        <div id="header">
                <h1>
                </h1>
        </div>
       <form name="forma"> 
       <input maxlength="250" size="55" id='inq' name="q" value="" /><br />
 	</form>

	<div id=result></div>
        <p><strong>Design</strong> &copy 2011</p>
    </div>
        
</body>
</html>

