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

