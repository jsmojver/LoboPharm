qz.security.setCertificatePromise(function(resolve, reject) {
	//Alternate method 1 - anonymous
	resolve();  // remove this line in live environment
});

qz.security.setSignatureAlgorithm("SHA512"); // Since 2.1
qz.security.setSignaturePromise(function(toSign) {
	return function(resolve, reject) {
		//Alternate method - unsigned
		resolve(); // remove this line in live environment
	};
});


/// Connection ///
function launchQZ() {
	if (!qz.websocket.isActive()) {
		//Retry 5 times, pausing 1 second between each attempt
		startConnection({ retries: 5, delay: 1 });
	}
}

function startConnection(config) {
	if (!qz.websocket.isActive()) {
		qz.websocket.connect(config).then(function() {
			findVersion();
		}).catch(handleConnectionError);
	} else {
		displayMessage('An active connection with QZ already exists.', 'alert-warning');
	}
}

function endConnection() {
	if (qz.websocket.isActive()) {
		qz.websocket.disconnect().then(function() {
		}).catch(handleConnectionError);
	} else {
		displayMessage('No active connection with QZ exists.', 'alert-warning');
	}
}

var qzVersion = 0;
function findVersion() {
	qz.api.getVersion().then(function(data) {
		qzVersion = data;
		displayVersion();
	}).catch(displayError);
}

function displayVersion() {
	displayMessage("qz-version:" + qzVersion, "");
//	window.alert("qz-version:" + qzVersion);
}

/// Detection ///
function findPrinter(query, set) {
	qz.printers.find(query).then(function(data) {
//		displayMessage("<strong>Found:</strong> " + data);
		if (set) { setPrinter(data); }
	}).catch(displayError);
}

function setPrinter(printer) {
	var cf = getUpdatedConfig();
	cf.setPrinter(printer);
}

/// QZ Config ///
var cfg = null;
function getUpdatedConfig(cleanConditions) {
	if (cfg == null) {
		cfg = qz.configs.create(null);
	}

	updateConfig(cleanConditions || {});
	return cfg
}

function updateConfig(cleanConditions) {
	var copies = 1;

	cfg.reconfigure({
						copies: copies,
					});
}

function includedValue(value) {
	if (value != null) {
		return value;
	} else {
		return undefined;
	}
}

function printHex(hexdata) {
	var config = getUpdatedConfig();

	var printData;
	printData = [
		{ flavor: 'hex', data: hexdata },
	];

	qz.print(config, printData).catch(displayError);
}

function printHexOnPrinter(printer_query, hexdata) {
	qz.printers.find(printer_query).then(function(data) {
		setPrinter(data);
		printHex(hexdata);
	}).catch(displayError);
}

function handleConnectionError(err) {
	if (err.target != undefined) {
		if (err.target.readyState >= 2) { //if CLOSING or CLOSED
			displayError("Connection to QZ Tray was closed");
		} else {
			displayError("A connection error occurred, check log for details");
			console.error(err);
		}
	} else {
		displayError(err);
	}
}

function displayError(err) {
	console.error(err);
	displayMessage(err, 'alert-danger');
}

function displayMessage(msg, css, time) {
	window.alert(css + ":" + msg);
}
