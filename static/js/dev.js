function light_off(){
    let is_on = document.getElementById("top");
    let but = document.getElementById("but");
        but.classList.toggle("on");
    if (but.classList.contains("on")){
        but.innerText = "on";
        is_on.style.backgroundColor = "yellow";
        is_on.style.border = "none";
    }
    else {
        but.innerText = "off";
        is_on.style.backgroundColor = "black";
    };
};
let back = document.createElement("label");
let btn = document.createElement("input");
let spin = document.createElement("div");
btn.type = "checkbox";
btn.style.display="none";
spin.className = "slider";
back.className = "tonggle";
btn.className = "tbtn";
let is_day = "flase";
btn.addEventListener("change", function () {
    if (is_day=="True"){
        document.body.style.backgroundColor = "black";
        document.body.style.color = "white";
        is_day= "flase";
        spin.style.transform = "translatex(72px)";
        
    }else{
        document.body.style.backgroundColor = "white";
        document.body.style.color = "black";
        is_day= "True";
        spin.style.transform = "translatex(0px)";
    };
});
document.body.appendChild(back);
back.appendChild(btn);
back.appendChild(spin);
