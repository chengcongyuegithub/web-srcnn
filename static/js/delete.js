$(document).ready(function(){
  $("#content").on('click','.delete',function(e){
      var picId=$(e.target).parent().attr("id");
      var sub=picId.indexOf('_');
      var pictureId=picId.substring(0,sub);
      var pictureAction=picId.substring(sub+1);
      if(pictureAction=='Origin')
      {
          var con=confirm("你选择是原图,点击删除将会删除其所有相关资源");
          if(!con)
          {
              return ;
          }
      }
      $.ajax({
            url: '/delete',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify({
                pictureId:pictureId,
                pictureAction:pictureAction
            }),
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            contentType: 'application/json; charset=utf-8',
            success: function (res) {
                //alert(res['code']+" "+res['message']);
                if(res['code']=="200")
                {
                    window.parent.opener.location.reload();
                    window.close();
                }else
                {
                    var picId=res['pictureId']+"_"+res['pictureAction'];
                    $("#"+picId).parent().remove();
                }
            }
        })
  });
});