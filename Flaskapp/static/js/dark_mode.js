function dark(){
    var element = document.body;
    let cur_attrib=element.getAttribute("class");
    sessionStorage.setItem("toggle_checked", document.getElementById("toggle_switch").checked);
    var page_flag=0;
    try{
        var ques1 = document.getElementById("Q1");
        var children1 = ques1.children;
        var ques2 = document.getElementById("Q2");
        var children2 = ques2.children;
        var ques3 = document.getElementById("Q3");
        var children3 = ques3.children;
        if(ques1!==null){
            page_flag=1;
        }
    }
    catch (error) {
        console.log("Error", error);
    }
    
   
    if (cur_attrib.endsWith("light")){
        if(page_flag){
            for (let i = 0; i < children1.length; i++) {
                var child = children1[i];
                child.id = "Main_ques2";
            }
            for (let i = 0; i < children2.length; i++) {
                var child = children2[i];
                child.id = "Main_ques2";
            }
            for (let i = 0; i < children3.length; i++) {
                var child = children3[i];
                child.id = "Main_ques2";
            }
        }
        
        element.setAttribute("class", "d-flex flex-column h-100 bg-dark");
    }
    else{
        element.setAttribute("class", "d-flex flex-column h-100 bg-light");
        if(page_flag){
            for (let i = 0; i < children1.length; i++) {
                var child = children1[i];
                child.id = "Main_ques1";
            }
            for (let i = 0; i < children2.length; i++) {
                var child = children2[i];
                child.id = "Main_ques1";
            }
            for (let i = 0; i < children3.length; i++) {
                var child = children3[i];
                child.id = "Main_ques1";
            }
        }
        
    }

    try{
        var nav_elem = document.getElementById("nav1");
        if(nav_elem!==null){
            nav_elem.id="nav2";
        }
        else{
            var nav_elem = document.getElementById("nav2");
            nav_elem.id = "nav1";
        }
    }
    catch(error){
        console.log("Error",error);
    }
   
}

function Find_cur_theme(){
    var cur_body=document.body;
    var cur_theme=cur_body.getAttribute("class");
    sessionStorage.setItem("class",cur_theme);
    sessionStorage.setItem("togge_checked", document.getElementById("toggle_switch").checked);
}

function set_theme(){
   
    var temp=sessionStorage.getItem("toggle_checked");
    console.log(temp);
    if(temp==null || temp==String(false)){
        document.getElementById("toggle_switch").checked =false;
        sessionStorage.setItem("toggle_checked",false);
    }
    else{
        document.getElementById("toggle_switch").checked = true;
        sessionStorage.setItem("toggle_checked", true);
        dark();
    }
    
    
    Check_For_Login_Default();
}


function set_theme_Profile_Page() {

    var temp = sessionStorage.getItem("toggle_checked");
    console.log(temp);
    if (temp == null || temp == String(false)) {
        document.getElementById("toggle_switch").checked = false;
        sessionStorage.setItem("toggle_checked", false);
    }
    else {
        document.getElementById("toggle_switch").checked = true;
        sessionStorage.setItem("toggle_checked", true);
        dark();
    }

    Check_For_Login();
}
