$(function(){

	$('#search_prescription').keyup(function() {
		$.ajax({
			type: "POST",
			url: "search_prescription/",
			data: {
				'search_text': $('#search_prescription').val(),
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
			},
			success: searchSuccess,
			dataType: 'html'
		});
	});
});

function searchSuccess(data, textStatus, jqXHR){
	$('#search-results').html(data)
}


function save_prescription(target, ordercode){

	$ajax({
		type: "POST",
		url: "save_prescription/",
		data: {
			'save_text': ordercode,
			'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
		},
		success: saveSuccess,
		datatype: 'html'
	});

}

function saveSuccess(data, textStatus, jqXHR){

}
