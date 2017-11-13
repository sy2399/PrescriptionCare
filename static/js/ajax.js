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

	$('#search-disease-results').on({
	    mouseenter : function(){
	        var tr = $(this);
            var td = tr.children();//선택한 상병값
            td.eq(0).css("background-color", "#abd9e9");
            var pre_td = td.eq(1);
            //여기서 ajax로 관련처방리스트 불러서 아래의 pre_td.text()안에 넣으면댐
            pre_td.text(td.text())

	    },
	    mouseleave: function(){
	        var tr = $(this);
            var td = tr.children();//선택한 상병값
            var pre_td = td.eq(1);
            td.eq(0).css("background-color", "#ffffff");
            pre_td.text("")
	    }

	}, "tr");
});

function prescriptionSearchSuccess(data, textStatus, jqXHR){
	console.log(data);
	$('#search-prescription-results').html(data);
}

function diseaseSearchSuccess(data, textStatus, jqXHR){
	console.log(data);
	$('#search-disease-results').html(data);
}

