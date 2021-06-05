const socket = io();
//socket.emit("message", "hello");

socket.on("message", function (msg, user) {
  console.log($("#messages").val());
  $("#messages").append("<li>" + msg + "</li>");
});

$("#send").on("click", function () {
  socket.send($("#myMessage").val());
  $("#myMessage").val("");
});
