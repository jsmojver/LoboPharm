//////////// Globalne varijable /////////////////

var lastSearchUrl;

//////////////////////////////////////////////////

function sticky_notify_order(id, title, content) { return $.gritter.add({ title: title, text: content, image: '/static/img/arrowbox.png', sticky: false, time:5000, class_name: 'bubble-'+id}); }
// function sticky_notify_remove(id) {  $.gritter.remove(id); } // ID vraca sticky_notify_order, to je zadnji dio id-a tog objekta u DOM-u
function sticky_notify_remove(zahtjev_id) { try {tmp = $('.bubble-'+zahtjev_id).attr('id').split('-');} catch(err){return;} id = parseInt(tmp[tmp.length - 1]); $.gritter.remove(id); } // ID vraca sticky_notify_order, to je zadnji dio id-a tog objekta DOM-u

function info_notify(title, content) { return $.gritter.add({ title: title, text: content, image: '/static/img/devel/submit3.png', time:1500, sticky: false, class_name: 'bubble-info-1'}); }
function info_warning(title, content) { return $.gritter.add({ title: title, text: content, image: '/static/img/devel/alert2.png', time:1500, sticky: false, class_name: 'bubble-info-1'}); }
function info_notify_short(title, content) { return $.gritter.add({ title: title, text: content, image: '/static/img/devel/submit3.png', time:750, sticky: false, class_name: 'bubble-info-1'}); }

function get_active_tab() { return $("#mainTabs").tabs('option', 'selected'); }
function refresh_active_tab() { $("#mainTabs").tabs( "load" , get_active_tab()); }
function refresh_tab_izdavanje() {$("#mainTabs").tabs( "load" , 1);} 

function set_active_main_tab(number) { $("#mainTabs").tabs("select", number); }
function url_into_active_main_tab(url) { x = $("#mainTabs"); n=get_active_tab(); x.tabs('url', n, url); x.tabs('load', n); }
function url_into_main_tab(url, number) { x = $("#mainTabs"); x.tabs("url", number, url); x.tabs("load", number);}
function load_and_focus_tab(url, number) { set_active_main_tab(number); url_into_main_tab(url, number); } // Load and focus

function url_into_sub_tab(url, tab, number) { x = $("#insideTabs-"+tab); x.tabs("url", number, url); x.tabs("select", number); x.tabs("load", number);}

/* Under Development: */

function show_user(id) { load_and_focus_tab('/client/view/'+id, 0); }
function show_order(sifra) { load_and_focus_tab('/order/view/'+sifra, 2); } // Važno - ovo vraća view funkcija kao javascript, ne diraj
function show_cart() { load_and_focus_tab('/order/kosarica/view', 2);}
function show_meds_search() { load_and_focus_tab('/meds/search', 2);}
function show_meds_advanced_search() { load_and_focus_tab('/meds/search/advanced', 2);}
function show_meds_search_other() { load_and_focus_tab('/meds/search/drugotrziste/form', 2);}

/* Beep */

var beep_sound = new Audio("/static/sound/beep-8.wav"); // Promijeniti, lokacija za test da podržava premotavanje (django test server ne podržava)
var refresh_process_running = 0;

function beep() { beep_sound.play(); }


/* Printing */

print_plugin = '';
function zebra_print(msg, callback) {  console.log(print_plugin.print(msg)); callback(); }

function ispisi_shipping_label(broj) { 
  $.get("/order/print/shipping/label/" + broj, function(data){
    print_plugin.print(data);   
  });
}

function ispisi_potvrdu(broj) { 
  $.get("/order/print2/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_racun_za_pristigle(broj) { 
  $.get("/order/print/racun/za/pristigle/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_racun_njemacki(broj) { 
  $.get("/order/print/racun/njemacki/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_racun_njemacki_broj(broj) { 
  $.get("/order/print/racun/njemacki/broj/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_potvrda_njemacki(broj) { 
  $.get("/order/print/potvrda/njemacki/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_potvrda_o_uplati_njemacki(broj) { 
  $.get("/order/print/potvrda/o/uplati/njemacki/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_papiric_o_narudzbi(broj) { 
  $.get("/order/print/papiric/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_potvrdu_o_narudzbi(broj) { 
  $.get("/order/print/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_potvrdu_za_blagajnu(broj) { 
  $.get("/order/print/barcode/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_racun(broj) {
  $.get("/order/fiskaliziraj/racun/print/" + broj, function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_potvrdu_obracuna() {
  $.get("{% url fiskalizacija.obracun.dnevni %}", function(data){
    print_plugin.escpos(data);   
  });
}

function ispisi_naljepnice(posiljkalijek_id) { 
  $.get("/depo/posiljka/kutija/kodiraj/" + posiljkalijek_id, function(data){
    print_plugin.escpos(data);   
  });  
}

function update_tecajne_liste() {
  $.get("/hnb/tecajna", function(data){
    location.reload();
  });

}

function batch_ispis_racuna(start, stop) {
  print_notify(1, 'Sekvencijalni ispis', 'Preostalo: ' + (stop-start));
  batch_ispis_worker(start, stop);
}

function batch_ispis_worker(start, stop) {
         console.log(start, stop);
         print_notify_update('Sekvencijalni ispis', 'Preostalo: ' + (stop-start));          
         ispisi_racun_njemacki_broj(start);
         if(stop-start)          
           setTimeout(function(){batch_ispis_worker(start+1, stop);}, 2000);                                
         else {
	   print_notify_remove(1);
	   return;    
	}     
}

/* Notifications */

function notification_into_tab(text, type, number) { 
	tab = $('#mainTab-'+number); tab.prepend('<div class="message-wrapper ok"><p><strong>OK MESSAGE.</strong>' + text + '</p><a href="#" class="close full"><img SRC="/static/img/close.gif" title="Close the message" alt="close" onClick="notification_close(this);" /></a><div class="clear"></div></div>');
}

function notification_into_current_tab(text) {
	$('#mainTabs .ui-tabs-panel:not(.ui-tabs-hide)').prepend('<div class="message-wrapper ok"><p><strong>OK MESSAGE.</strong>' + text + '</p><a href="#" class="close full"><img SRC="/static/img/close.gif" title="Close the message" alt="close" onClick="notification_close(this);" /></a><div class="clear"></div></div>');
}

function notification_close(a) { $(a).closest('.message-wrapper').slideUp('slow', function(){$(this).remove();}); event.preventDefault(); } // Ok, ne diraj!

function notification_dialog(p_message, p_title) 
{ 
  p_title = p_title || ""; 
  $("<div>" + p_message + "</div>").dialog({ 
    title: p_title, 
    resizable: false, 
    modal : true, 
    overlay: { backgroundColor: "#000", opacity: 0.5 }, 
    buttons: { "Okay": function() { $(this).dialog("close"); } }, 
    close: function(ev, ui) { $(this).remove(); } 
  }); 
} 

/* Under heavy development */
////////////////////// MAKNUTI NA KRAJU /////////////////////////////////////
function debug_numelements() {
 console.log(document.getElementsByTagName('*').length);
}

function debug_numelements_refresh() {
 $('#debug-remove').html('debug: nr.elems: ' + document.getElementsByTagName('*').length);
}

function debug_test_printanja() {
    zebra_print('\nUN\nN\nq240\nA15,15,0,1,1,1,R,"     TESTIRAMO     "\nB12,40,0,E30,2,2,70,B,"1234567890128"\nP1,1\n', function(){
    console.log(print_plugin.echo('x').trim());
    console.log(print_plugin.echo('x').trim());
    console.log(print_plugin.echo('x').trim());
    console.log(print_plugin.status().trim());
    console.log(print_plugin.status().trim());
  });  
}

lijek_objekti = [];
kodovi=[];
naziv_lijeka = '';
ajax_printed_notify_flag=0;

function debug_print_click(event, id) {
    // console.log(event, id);
    kodovi=[];        /* Ako nema ovog, kod uzastopnih printanja printao bi i one stare jer polje nije obrisano */
    $.getJSON('http://127.0.0.1:8000/depo/posiljka/kutija/naljepnice/' + id, function(data){
      lijek_objekti=data;
      $.each(data, function(i, j){
            status = '';             
             kodovi.push(i);
            });
    if(!kodovi.length) {alert('Naljepnice su već otisnute!'); return}; /* Ako su sve naljepnice isprintane vrati se */
    kodovi.sort(); /* sortiraj, da je lakše nastaviti kad se prekine ? */
    naziv_lijeka  =  lijek_objekti[kodovi[0]];
    if(event.ctrlKey) {  /* ako je stisnut ctrl prilikom klikanja na link, printaj u kontinuitetu a ne jednu po jednu sa feedbackom */ /*TODO: negdje dodaj setiranje printed statusa, možda i rekurzivno pozivanje kao dolje pa nek čeka da prestane status biti 50 i tek onda zapiše da je sve ispravno ispisano! Koristi interni counter isprintanih naljepnica!  */
        msg = '\n';
        for(i=0;i<kodovi.length;i++)
            msg += 'N\nq240\nA8,15,0,1,1,1,R,"'+ naziv_lijeka + '"\nB12,40,0,E30,2,2,70,B,"11'+ kodovi[i] +'"\nP1,1\n';
            print_plugin.print(msg); /* pošalji sve na printer i sad pozovi supervise_batch_printing da polla status 50 dok ne završi i usporedi label counter */
            $.get('http://127.0.0.1:8000/depo/posiljka/kutija/naljepnice/svesuispisane/' + id);
        }
    else { 
            print_notify(1, naziv_lijeka, 'Preostalo: ' + kodovi.length);
            debug_do_printing(kodovi.length);                   
            }
     });
}

function error_status_parse(status) {
     if(status=='01') console.log('Syntax error');
     else if(status=='02') console.log('Exceeded label border');
     else if(status=='07') { print_notify_update('Upozorenje', 'Nema dovoljno naljepnica ili ribona!'); console.log('Nema naljepnica ili ribona');    }
     else if(status=='11') {  print_notify_update('Greška 11', 'Poklopac pisača je otvoren!');  console.log('Poklopac je otvoren');     }
     else if(status=='82') {  print_notify_update('Greška 82', 'Greška u senzoru ruba naljepnice!');  console.log('Greška 82');     }
     else if(status=='84') {  print_notify_update('Greška 84', 'Prebrzo uvlačenje medija!');  console.log('Greška 84');     }
     else if(status=='91') print_notify_update('Greška 91', 'Pisač nedostupan!'); 
     else if(status=='92') print_notify_update('Greška 92', 'Nije moguće pisati');
     else if(status=='93') print_notify_update('Greška 93', 'Nedostupan za čitanje!');
     else if(status=='94') print_notify_update('Greška 94', 'Nije moguće pročitati status!');
     else if(status=='95') print_notify_update('Greška 95', 'Nije moguće pročitati status!');
     else if(status=='96') print_notify_update('Greška 96', 'Pisač ne odgovara!');
     else console.log('Nepoznata greška ', status);
}

function debug_do_printing(depth) { /* Rekurzivna funkcija koja preko setTimeout i citanja statusa pokusava isprintati sve naljepnice iz queuea, nakon svake salje potvrdu da je ispisana */    
     status = print_plugin.status().trim();       
     if(status == '00') {                    
           if (!depth) { // Da se vraća samo iz OK stanja, inače rekurzija ne izvrši zadnji busy i ne dojavi da je ispisan
                  print_notify_remove(1);
                  status = print_plugin.status().trim();     // Pročitaj status, ako je ostao na 01 vratit će se na 00
                  return;
                   }
            else { 
                      //console.log('Printer OK');
                      ajax_printed_notify_flag = 1; // Kad je printer spreman, postavi se flag da prvi ulaz u status 50 dojavi da je naljepnica isprintana
                      print_notify_update(naziv_lijeka, 'Preostalo: ' + depth);          
                      print_plugin.print('\nN\nq240\nA8,15,0,1,1,1,R,"'+ naziv_lijeka + '"\nB12,40,0,E30,2,2,70,B,"11'+ kodovi[depth-1] +'"\nP1,1\n');
                      setTimeout(function(){debug_do_printing(depth-1);}, 100);                                
                }
          }
     else if (status=='50') {  if(ajax_printed_notify_flag) {ajax_printed_notify_flag=0; $.get('http://127.0.0.1:8000/depo/posiljka/kutija/naljepnice/ispisana/'+kodovi[depth]);}
         setTimeout(function(){debug_do_printing(depth);}, 100);  } /* Ako je printer busy, nemoj smanjivati indeks polja broja koji printamo i tu možda ugradi promjenu statusa koda ajaxom, ako je busy onda je valjda isprintano ali pazi da se ne izvršava previše puta (10 puta u sekundi je ovo) - neki lokalni flag da se izvrši samo jednom kad status postane 50 ! */               
     else error_status_parse(status);
     return;         
}

function ispisi_jednu_naljepnicu(id, naziv, url) {
    naziv_lijeka = naziv;
    for(i=0; i<parseInt((22-naziv.length)/2); i++) naziv_lijeka = ' ' + naziv_lijeka;
    for(i=1; i<(22-naziv.length); i++) naziv_lijeka = naziv_lijeka + ' ';
    
     kodovi=[]; kodovi.push(id);
     debug_do_printing(1);
     load_and_focus_tab(url, 1);
}

function print_notify(id, title, content) { return $.gritter.add({ title: title, text: content, image: '/static/img/devel/printer2.png', sticky: true, class_name: 'print-'+id}); }
function print_notify_customimg(id, title, content, img) { return $.gritter.add({ title: title, text: content, image: img, sticky: true, class_name: 'print-'+id}); }
function print_notify_remove(zahtjev_id) { try {tmp = $('.print-'+zahtjev_id).attr('id').split('-');} catch(err){return;} id = parseInt(tmp[tmp.length - 1]); $.gritter.remove(id); } // ID vraca sticky_notify_order, to je zadnji dio id-a tog objekta u 
function print_notify_update(title, text) { $('.print-1 .gritter-title').html(title); $('.print-1 .gritter-with-image p').html(text); }

///////////////////////////////////////////////////////////
//		Fiskalizacija				//

function jir_format_test(jir) {
	rx=/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/g;
	return rx.test(jir);
}

function fiskaliziraj(order_id) {
	info_notify('Obavijest', 'Spajam se na server Porezne Uprave...');
	// Prvo provjera veze servera i PU, neki poziv koji vrati delta t između echo poziva koje periodički radi server
	$.ajax({
	    url: "/order/json/fiskaliziraj/racun/" + order_id,
	    type: "GET",
	    dataType: "json",
	    timeout: 4000,
	    success: function(data) { 
			console.log('Exec time: ' + data.exec_time);			
			console.log('Greska: ' + data.greska);
			// TODO: negdje logiraj tu grešku na serveru uz račun!
			$.getJSON('/fiskalizacija/json/racun/detail/' + data.racun_id, function(d) {
			if(jir_format_test(d.jir)) {
				info_notify('Uspješno fiskaliziran', d.jir);
				}
			else {
				info_notify('Greška', 'Prekid veze ili greška PU. <br />Račun se smatra IZDANIM!!!');
				}
			ispisi_racun(d.racun);
			url_into_active_main_tab('/order/view/' + order_id);				
			//console.log('Ispisat ću račun, štedimo papir.');
			});	
		},
	    error: function(x, t, m) {
		// tu utrpaj rekurzivno pozivanje!	
		info_notify('Greška', 'Nije moguće kontaktirati server');
		return 0;
	    }
	});

//	    donji getJSON kod ide TU u callback inače bi se izvršio prije reda
	// račun iz narudžbe kreiraj i onda ga kreni fiskalizirati 3 put po 2 sekunde, ako ne upali - jebiga, ispiši samo ZKI i flagaj da je problematičan i da bu se kasnije otisnuo, promijeni i poruku koju ispisuje na račun umjesto JIR
	// Tu sad sa setTimeout 10 brzih periodickih provjera za JIR po ID-u racuna, ako ne dodje ponovi sve do max 3put i onda odustani i ispisi samo ZIK a racun oznaci za kasniju dostavu jer ne radi nesto
	// $.getJSON nešto, u templateu sa generičkim viewom generiramo JSON kod kojim javascript funkciji dostavljamo podatke
}

function akontacija(order_id) {
	info_notify('Obavijest', 'Spajam se na server Porezne Uprave...');
	// Prvo provjera veze servera i PU, neki poziv koji vrati delta t između echo poziva koje periodički radi server
	$.ajax({
	    url: "/order/json/akontacija/racun/" + order_id,
	    type: "GET",
	    dataType: "json",
	    timeout: 4000,
	    success: function(data) { 
			$.getJSON('/fiskalizacija/json/racun/detail/' + data.racun_id, function(d) {
			if(jir_format_test(d.jir)) {
				info_notify('Akontacija fiskalizirana', d.jir);
				}
			else {
				info_notify('Greška', 'Prekid veze ili greška PU. <br />Račun se smatra IZDANIM!!!');
				}
			ispisi_racun(d.racun);
			url_into_active_main_tab('/order/view/' + order_id);				
			});	
		},
	    error: function(x, t, m) {
		// tu utrpaj rekurzivno pozivanje!	
		info_notify('Greška', 'Nije moguće kontaktirati server');
		return 0;
	    }
	});
}

function storniraj(racun_id) {
	info_notify('Obavijest', 'Spajam se na server Porezne Uprave...');
	// Prvo provjera veze servera i PU, neki poziv koji vrati delta t između echo poziva koje periodički radi server
	$.ajax({
	    url: "/order/json/storniraj/racun/" + racun_id,
	    type: "GET",
	    dataType: "json",
	    timeout: 6000,
	    success: function(data) { 
			console.log('Exec time: ' + data.exec_time);			
			console.log('Greska: ' + data.greska);
			// TODO: negdje logiraj tu grešku na serveru uz račun!
			$.getJSON('/fiskalizacija/json/racun/detail/' + data.racun_id, function(d) {
			if(jir_format_test(d.jir)) {
				info_notify('Uspješno storniran', d.jir);
				}
			else {
				info_notify('Greška', 'Prekid veze ili greška PU. <br />Račun se smatra STORNIRANIM!!!');
				}
			//Stornirani se ne ispisuje, nema smisla
				load_and_focus_tab('/fiskalizacija/racun/view/' + data.racun_id, 2);
			});	
		},
	    error: function(x, t, m) {
		// tu utrpaj rekurzivno pozivanje!	
		info_notify('Greška', 'Nije moguće kontaktirati server');
		return 0;
	    }
	});
}

function izdaj_nevezan_fiskalni() { // Legacy funkcija
	info_notify('Obavijest', 'Spajam se na server Porezne Uprave...');
	$.ajax({url: "/fiskalizacija/racun/add/", type: "GET", dataType: "json", timeout: 6000,
	    success: function(data) { 
			$.getJSON('/fiskalizacija/json/racun/detail/' + data.racun_id, function(d) {
			if(jir_format_test(d.jir)) {
				info_notify('Uspješno fiskaliziran', d.jir);
				}
			else {
				info_notify('Greška', 'Prekid veze ili greška PU. <br />Račun se smatra IZDANIM!!!');
				}
			ispisi_racun(d.racun);
			url_into_active_main_tab('/fiskalizacija/racun/view/' + data.racun_id);
			});	
		},
	    error: function(x, t, m) {
		info_notify('Greška', 'Nije moguće kontaktirati server');
		return 0;
	    }
	});
}


////////////////////// Naknadna dostava računa ///////////

function fiskaliziraj_dostavi_naknadno() {
      $.getJSON('/fiskalizacija/json/neuspjesni/list/', function(data) {
		// info_notify('Dostavljam', data.length);
		list = new Array();
		$.each(data, function(key, val) { if(key!='xx') list.push(parseInt(key)); }); // Ne smije biti 00, to smo dodali jer JSON ne smije imati trailing comma :)
		print_notify_customimg(1, 'Naknadna dostava računa', 'Preostalo: ' + list.length, '/static/img/devel/racun.png');
	 	dostavi_recursive(list, 1);	
	});
}

function dostavi_recursive(lista, gritter_id, orig_len) {
	if(lista.length) { 
		print_notify_update('Naknadna dostava računa', 'Preostalo: ' + lista.length);
		x = lista.pop();
                $.ajax({url: "/fiskalizacija/racun/dostavi/naknadno/" + x, type: "GET", dataType: "json", timeout: 6000,
                    success: function(d) {
		    if(d.status=='failed') {
                        info_warning('Greška', 'Račun nije uspješno dostavljen');
                    	dostavi_recursive(lista, gritter_id);
			}
	            else {
			setTimeout(function(){dostavi_recursive(lista, gritter_id);}, 1000); // da baš ne jašemo server porezne
                        info_notify_short('OK', 'Račun br. ' + x + ' uspješno dostavljen!<br>' + d.jir);
		    }
		  },
                   error: function(x, t, m) { info_notify('Greška', 'Nije moguće kontaktirati server'); return 0; }
               });
            }
	else {
		print_notify_remove(gritter_id);
	        load_and_focus_tab('/fiskalizacija/racun/list', 2);
	     }
}	

///////////////////////////////////////////////////////////

/* Ovo je za glavni search bar
function autocomplete(object) {
	$('#search-field').autocomplete({  
          		source: "/meds/autocomplete",
			minLength: 3,
			select: function( event, ui ) {
			    load_and_focus_tab('/meds/search/begins/' + ui.item.value, 2)
			    $(this).val('');
			}
        });
}
 */
 
 function na_stanju_izdavanje(id) {
     console.log('pozvano! ', id);
 	   $('#podaci-o-lijeku').load('/ajax/izdavanje/olijeku/' + id);
 	   $('#id_kolicina').focus();
 }
 
var tmptest='';

function universal_autocomplete(object) {
  $(object).autocomplete({
      source: $(object).data('autocomplete-url'),
      minLength: 3,
      select: function(event, ui) {
        tmptest = $(object);        
        if(typeof ui.item.id != 'undefined')
          $(object).blur().val(ui.item.id.toString()); // Pokušaj poslati ID
        else
          $(object).blur().val(ui.item.value.toString()); // Ako ID nije postavljen, pošalji vrijednost
        $(object).data('autocomplete-value', ui.item.id);
        if(callback = $(object).data('autocomplete-callback')) // u data-autocomplete-callback utrpamo funkciju koju pozove autocomplete kad obavi svoje :)
              eval(callback);
      }
  }); 
}

function setup_sata() {
      setInterval( function() {
      var seconds = new Date().getSeconds();
      var sdegree = seconds * 6;
      var srotate = "rotate(" + sdegree + "deg)";

      $("#sec").css({"-moz-transform" : srotate, "-webkit-transform" : srotate});

      }, 1000 );

      setInterval( function() {
      var hours = new Date().getHours();
      var mins = new Date().getMinutes();
      var hdegree = hours * 30 + (mins / 2);
      var hrotate = "rotate(" + hdegree + "deg)";

      $("#hour").css({"-moz-transform" : hrotate, "-webkit-transform" : hrotate});

      }, 1000 );

      setInterval( function() {
      var mins = new Date().getMinutes();
      var mdegree = mins * 6;
      var mrotate = "rotate(" + mdegree + "deg)";

      $("#min").css({"-moz-transform" : mrotate, "-webkit-transform" : mrotate});

      }, 1000 );
}



$(document).ready(function() {
    print_plugin = document.getElementById('print_plugin');
    show_meds_search();
    // autocomplete();

{% if perms.depo %}
    setInterval("polling()", 5000);
{% endif %}

{% if perms.fiskalizacija %}
    setInterval("status_veze()", 11000);
{% endif %}

//    setInterval("polling_debug()", 2000);    
//    setInterval("get_temp()", 3000);

    get_temp();
   
    inventura = '';
    
    setup_sata();

 // search box
  $('#search-box').submit(function (event) {
    event.preventDefault();   
    value = $('#search-field').val();
    $('#search-field').val('');
    if (!isNaN(value)) // ako je upisan broj, tretiraj ga kao bar kod, inače za izdavanje s depoa, pretraživanje pacijenta, lijeka ili tako nešto...
      if(value.isEan13())
          $.getScript('/barcode/submit/' + value);
       else alert('Neispravan barkod, provjerite unos!'); // tu možda pokreni pretraživanje ili dohvaćanje pacijenata, nešto...
    else if (value[0].toLowerCase() == 'p') {
          url_into_active_main_tab('/order/view/sifra/' + value.substr(1));
      }
      
    });

    
    String.prototype.isEan13 = function(){ if (isNaN(this)) return false; s=(this.slice(0,-1)); c=(s+0).split('').reverse(); n=0; for(var i in c){n+=(i%2)?c[i]*3:+c[i]}; return this==(s+((10-(n%10))%10)) }
    String.prototype.isUPC12 = function() { if (isNaN(this) || this.length != 12) return false; return (0+this).isEan13(); }
    String.prototype.isPZN = function() { cd=this.slice(-1); if(this[0]=="-") pzn=this.slice(1,-1); else pzn=this.slice(0, -1); if(isNaN(pzn)) return false; if(pzn.length==6) pzn="0".concat(pzn); x = pzn.split('').reverse().map(function(x){return parseInt(x)}); mul=7; n=0; while(x.length){n+=x.shift()*mul; mul--;}; if(n%11==parseInt(cd)) return true; else return false;}

    // Keypress handleri za citac

    keycode = ''; kbtimestamp = new Date().getTime();
 
    $(document).keyup(function(e) {
           if(e.which == 39) { $('.ui-tabs-panel:not(.ui-tabs-hide) .paginator-desno').click(); return false; }
           else if(e.which == 37) { $('.ui-tabs-panel:not(.ui-tabs-hide) .paginator-lijevo').click(); return false; }
           // else if(e.which == 118) load_and_focus_tab('/depo/zahtjev/izdavanje', 1); // F7 - zahtjev za izdavanje DEPO
           else if(e.which == 118) show_cart(); // F7 - Košarica 
           else if(e.which == 119) 
		if(e.ctrlKey) 
			load_and_focus_tab('/client/browse', 0);
		else
			load_and_focus_tab('/client/search', 0); // F8 - pretraživanje pacijenata
           else if(e.which == 120) 
                if(e.ctrlKey && e.shiftKey) load_and_focus_tab('{% url depo.zahtjev.izdavanje %}', 2);            
		else if(e.ctrlKey) show_meds_search_other();
		else if(e.shiftKey) show_meds_advanced_search();
	 	else show_meds_search(); // F9 - pretraživanje lijekova njemačka

           else if(e.which == 121) load_and_focus_tab('/client/create', 0); // F10 - dodavanje osobe
           
           // plus i minus mijenjaju količinu na "DODAJ U KOŠARICU"
           else if(e.which ==107) increment_input_number();
           else if(e.which == 109) decrement_input_number();
           else if(e.which == 106) $('.dodaj-u-kosaricu').submit();
           
           if(document.body == document.activeElement) {
                 if(e.which == 73) console.log('stisnuto je i'); // Tu idu keyboard shortcuts za program koje se inače koriste za unos teksta                       
           }
    });   

    $(document).keypress(function(e)
    {
	if(document.body == document.activeElement) {// ako nista nema fokus onda detektiramo barcode, inače puštamo da unos ide u aktivno input polje ... zašto ovo??
             if ((e.which > 47 && e.which < 58) || e.which == 13 || e.which == 222) { // stisnut je broj, enter ili ' (PZN)
                        now = new Date().getTime(); 
                        if((now-kbtimestamp)<50) { 
                                if(e.which == 13 && keycode.isEan13()) { // tu još dodati provjeru za PZN 
                                //keycode = keycode.slice(0, -1);
                             					$.getScript('/barcode/submit/' + inventura + keycode).done(function(script, textStatus){/*console.log(textStatus);*/}).fail(function(a,b,c){});
                            					keycode=''; 
                            					beep();
                      					} 
				else if(e.which == 13 && keycode.isPZN()) {load_and_focus_tab('/meds/view/pzn/' + keycode, 2);}
				else keycode += String.fromCharCode(e.charCode); 
                                kbtimestamp = now; return false;
                         }
                         else { keycode='' + String.fromCharCode(e.charCode); kbtimestamp = now;  }
                }
	     }               
        });

});

function sakrij_formu_za_izdavanje() {
	x = $( "#izdavanje-accordion" );
	if(x.is(':visible')) x.slideToggle('slow');
}
function toggle_formu_za_izdavanje() { $('#izdavanje-accordion').slideToggle('slow'); }

function preuzmi(obj) {
	console.log(obj);
}


function trazilica_lijekova() {
  
}


/* test */

function test_redomat() {
  tmp=$('#semafor'); tmp.html(parseInt(tmp.html())+1);
}

function pos_brojcanik(iznos) {
  $('#brojcanik').html('<br /><br />' + iznos + ' &#8364;');
}

/* test */

temperature_alarm = 0;
tmax1 = 28.00;
tmin1 = 22.50;
tmax2 = 28.00;
tmin2 = 22.50;

function polling() {
 	// return false; //tmp fix
	$.getScript("/ajax/izdavanje/polling");
}

function get_temp() { // TODO: histereza u provjeru
  $.getJSON('/static/tempdata/temp.html', function(data){
     var t1=parseFloat(data['t1']); var t2=parseFloat(data['t2']);
     if (t1<tmin1 || t1>tmax1 || t2<tmin2 || t2>tmax2) {  // ako bilo koji odstupa (OR)
       if(!temperature_alarm) {
         info_warning('Upozorenje', 'Temperatura hladnjaka van dopuštenih granica!');
         beep();
         temperature_alarm = 1;
         $('#termometar-slika').attr('src', '/static/img/devel/temperature-warning.png');                 
         $('#termometar-box').effect("shake", { times:2 }, 120); 
          }
     }
     else if(t1>=(tmin1+0.25) && t1<=(tmax1-0.25) && t2>=(tmin2+0.25) && t2<=(tmax2-0.25) && temperature_alarm) { // svi su OK a bio je alarm, prešli smo prag histereze
          $('#termometar-slika').attr('src', '/static/img/devel/termometar.png');
          info_notify('Obavijest', 'Temperatura hladnjaka normalizirana!');
          temperature_alarm = 0;
        }
     $('#temp_friz_1').html(t1.toFixed(2));
     $('#temp_friz_2').html(t2.toFixed(2));
  });
}

function status_veze() {
  $.getJSON('{% url sysapp.provjeri.vezu %}', function(data){
    if(data['cis']) $('#status_cis').html('DA'); else $('#status_cis').html('NE');
    if(data['net']) $('#status_net').html('DA'); else $('#status_net').html('NE');
    if(data['vpn']) $('#status_vpn').html('DA'); else $('#status_vpn').html('NE');
   });
}

function polling_debug() {
  debug_numelements_refresh();
  $.getScript('{% url sysapp.ajax.polling %}');
}

function naslovna_kosarica_reload() {
	$('#kosarica_gore').load('/order/kosarica/naslovna');
}

function izdavanje_toggle_red(e) {
   $(e).toggleClass('odgodi-izdavanje');
}

function checkbox_toggle(obj, id) {  $.get("/order/artikal/izdati/toggle/" + id); }

function increment_input_number() {
    var a = $('.plusminus'); a.val(parseInt(a.val())+1); 
}

function decrement_input_number() {
        var a = $('.plusminus'); if(a.val() != '0') a.val(parseInt(a.val())-1); 
}

function odjava() {
  $.get('/accounts/logout', function(d) {
    window.open('','_self',''); 
    window.close(); 
  }); 
}

function inline_price_edit(a) {
  
}
