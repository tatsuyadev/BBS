$(function(){
  $('.tag').on('click',function(e){
    var v= $('#message').val();
    var selin = $('#message').prop('selectionStart');
    var selout = $('#message').prop('selectionEnd');
    var befStr="{"+$(this).val()+"}";
    var aftStr="{/"+$(this).val()+"}";
    var v1=v.substr(0,selin);
    var v2=v.substr(selin,selout-selin);
    var v3=v.substr(selout);
    $('#message')
      .val(v1+befStr+v2+aftStr+v3)
      .prop({
        "selectionStart":selin+befStr.length,
        "selectionEnd":selin+befStr.length+v2.length
        })
      .trigger("focus");
  });
});