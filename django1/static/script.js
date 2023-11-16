function sendData(Nr, Tat, Wert) {
	let formData = new FormData();
	formData.set('csrfmiddlewaretoken', "{{csrf_token}}");
	formData.set('Nr', Nr);
	formData.set('Tat', Tat);
	formData.set('Wert', Wert);
	fetch('/', { method: 'POST', body: formData });
}