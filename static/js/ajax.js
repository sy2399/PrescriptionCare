
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
		var tmp = " " + td.eq(1).text().split(" ")[0]
       $(this).siblings().css("background-color", "white");
       $(this).css("background-color", "#D3FFFE");

		$.ajax({
			type: "POST",
			url: "search_disease/",
			data: {
				'search_list':tmp,

				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
			},
			success: diseaseSearchSuccess,
			dataType: 'html'
		});
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

    $('#list_reset_button').click(function(){
        $('#clickResultView').val("");
    });
});

function prescriptionSearchSuccess(data, textStatus, jqXHR){
	$('#preResultDiv').html(data);
}

function diseaseSearchSuccess(data, textStatus, jqXHR){
    $('#loading').attr('style', 'visibility:hidden');
	$('#resultDiv').html(data);
}

function connectionSearchSuccess(data, textStatus, jqXHR){
	$('#search--results').html(data);
}
