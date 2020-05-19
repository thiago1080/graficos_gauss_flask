function redir(url){
    location.replace(url)
}
function myFunction(){
  var myvar
  myvar = setTimeout(showPage, 3000);
}

function showPage(){
  document.getElementById("loader").style.display = "none";
  document.getElementById("maindiv").style.display = "block";
  var container = document.getElementById("maindiv");
  var content = container.innerHTML;
  container.innerHTML= content; 
}

