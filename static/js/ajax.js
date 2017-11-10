$(function(){
	$('#search_prescription').keyup(function() {
		$.ajax({
			type: "POST",
			url: "search_prescription/",
			data: {
				'search_text': $('#search_prescription').val(),
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
			},
			success: prescriptionSearchSuccess,
			dataType: 'html'
		});
	});

    $('#search-prescription-results').on("click", "tr", function(){
    	var tr = $(this);
		var td = tr.children();
		$('#clickResultView').val($('#clickResultView').val() + td.eq(1).text());
    });

	$('#list_form_button').click(function(){
		$.ajax({
			type: "POST",
			url: "search_disease/",
			data: {
				'search_list': $('#clickResultView').val(),
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
			},
			success: diseaseSearchSuccess,
			dataType: 'html'
		});
	});
});

function prescriptionSearchSuccess(data, textStatus, jqXHR){
	console.log(data);
	$('#search-prescription-results').html(data);
}

function diseaseSearchSuccess(data, textStatus, jqXHR){
	console.log(data);
	$('#search-disease-results').html(data);
}

