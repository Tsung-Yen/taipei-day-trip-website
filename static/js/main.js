var nexPage = null;
//完成連線
function getPageData(pagenum){
    let openUrl = "http://3.131.86.32:3000/api/attractions?page="+pagenum;
    fetch(openUrl).then(res=>res.json())
    .then((jsonData)=>{
        //當資料載入成功後將GIF移除
        if(jsonData!=null){
            let loadImg = document.querySelector(".load_spot");
            loadImg.style.display = "none";
        };
        nextPage = jsonData["nextPage"];
        let pageDataLen = jsonData["data"].length
        for(let i=0;i<pageDataLen;i++){
            let linknum = jsonData["data"][i]["id"]; //放入link url
            let name = jsonData["data"][i]["name"];
            let mrt = jsonData["data"][i]["mrt"];
            let category = jsonData["data"][i]["category"];
            let img = jsonData["data"][i]["images"];
            let images = filtImg(img);
            //create empty html tag
            let part = document.querySelector(".part");

            //add a div to Dom
            //add single box which contain image&textbox
            let spotDiv = document.createElement("div");
            spotDiv.className = "spot";
            // spotDiv.style.width = "280px";
            // spotDiv.style.height = "260px"

            //add url to spot(1.the first data in spot)
            let clicklink = document.createElement("a")
            clicklink.href = "http://3.131.86.32:3000/attraction/"+linknum;
            clicklink.className = "link";
            //add img(put it into <a> will let user can click the bounds inside the img size)
            let imgImg = document.createElement("img");
            imgImg.src = images;
            
            //add title name(2.sec data in spot)
            let nameP = document.createElement("div");
            nameP.className = "spotname";
            let nameText = document.createTextNode(name);

            //add text cube(3.thir data in spot)
            let cubeDiv = document.createElement("div");
            cubeDiv.className = "cube";

            //add first text to cube(first data in cube)
            let mrtP = document.createElement("div");
            mrtP.className = "mrt";
            let mrtText = document.createTextNode(mrt);

            //add Sec text to cube(Sec data in cube)
            let catP = document.createElement("div");
            catP.className = "cat";
            let catText = document.createTextNode(category);
            
            //container append spotDiv
            part.append(spotDiv);
            //put three data into spotDiv
            spotDiv.append(clicklink);
            clicklink.append(imgImg);
            spotDiv.append(nameP);
            nameP.append(nameText);
            spotDiv.append(cubeDiv);
            
            //put two p tag into cube
            cubeDiv.append(mrtP);
            mrtP.append(mrtText);
            cubeDiv.append(catP);
            catP.append(catText);
        }
    });
}
function clearDiv(){
    //將預先秀出的資料移除(移出div並在將原本的容器div命名玩className放回去)
    let delSpotDiv = document.querySelector(".part");
    delSpotDiv.remove();
    let container = document.querySelector(".container");
    let createPart = document.createElement("div");
    createPart.className = "part";
    container.append(createPart);
}
//使用者透過搜尋關鍵字獲得資料
let keyword = null;
let keywordhistory = null;      //如果使用者未滑玩所有頁面再次搜尋，比對上次關鍵字結果不同。將div移除
let kynextPage = null;
let kypage = 0;
function keywordSearch(){
    keyword = document.querySelector(".insert").value;
    if(keyword != keywordhistory ){
        clearDiv();
        kypage = 0;
    }else if(keyword == null){
        alert("關鍵字不存在")
    }
    //取得連線
    keywordhistory = keyword;
    let url = "http://3.131.86.32:3000/api/attractions?page="+kypage+"&keyword="+keyword;
    fetch(url).then((res)=>{
        return res.json()})
    .then((jsonData)=>{
        let error = jsonData["error"];
        if(error != true){
            let num = jsonData["data"].length;
            for(let i =0;i<num;i++){
                kynextPage = jsonData["nextPage"];
                let keywordId = jsonData["data"][i]["id"];
                let name = jsonData["data"][i]["name"];
                let mrt = jsonData["data"][i]["mrt"];
                let category = jsonData["data"][i]["category"];
                let img = jsonData["data"][i]["images"];
                let images = filtImg(img);
                //抓取標籤並塞入內部資料
                let container = document.querySelector(".part");
                let spotDiv = document.createElement("div");
                spotDiv.className = "spot";
                let keywordLink = document.createElement("a");
                keywordLink.href = "http://3.131.86.32:3000/attraction/"+keywordId;
                let imgImg = document.createElement("img");
                imgImg.src = images;
                let nameDiv = document.createElement("div");
                nameDiv.className = "spotname";
                let nameText = document.createTextNode(name);
                let cubeDiv = document.createElement("div");
                cubeDiv.className = "cube";
                let mrtDiv = document.createElement("div");
                mrtDiv.className = "mrt";
                let mrtText = document.createTextNode(mrt);
                let catDiv = document.createElement("div");
                catDiv.className = "cat";
                let catText = document.createTextNode(category);

                //將資料一個個放入對應的標籤中
                container.append(spotDiv);
                spotDiv.append(keywordLink);
                keywordLink.append(imgImg);
                spotDiv.append(nameDiv);
                nameDiv.append(nameText);
                spotDiv.append(cubeDiv);
                cubeDiv.append(mrtDiv);
                mrtDiv.append(mrtText);
                cubeDiv.append(catDiv);
                catDiv.append(catText);
            }
        }else{
            let message = jsonData["message"];
            let notfindSpot = document.querySelector(".part");
            notfindSpot.textContent = message;
            notfindSpot.style.height = "434px";
            notfindSpot.style.fontSize = "20px";
            notfindSpot.style.color = "rgb(128, 118, 118)";
            let mask = document.querySelector(".mask");
        }
        
    });
}
// //偵測使用者滑動狀況，如果以捲動到底部載入下一頁資料
// function scrollPos(){
//     window.addEventListener('scroll',function(){
//         if(window.scrollY+window.innerHeight+30 >= document.documentElement.scrollHeight){
//             //如果keyword有被搜尋則不繼續對page提出發送
//             if(keyword == null){
                
//                 if (nextPage<=26){
//                     getPageData(nextPage);
//                 }
//             }else{
//                 //當使用者關鍵字搜尋滑到底，停止載入
//                 if(kynextPage!="null"){
//                     kypage+=1;
//                     keywordSearch();
//                 }
//             }
//         }
//         // console.log(document.documentElement.scrollHeight);
//         // console.log(window.scrollY+window.innerHeight);
//     });
// }

//初始化函式:一載入頁面就直接秀出第一頁
// function initShow(){
//     getPageData(0);
//     // scrollPos();
// }
// initShow();
//以上部分為初始化第一頁資料

//過濾圖片函式(將第圖片不乾淨的字元過濾將其分割，並回傳第一張)
function filtImg(data){
    //取得第一張圖片
    let result = data.split(",",1);
    return result;
}
function init(){
    getPageData(0);
    //將input&button綁再一起
    let input = document.querySelector(".insert");
    input.addEventListener("keyup", function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            document.getElementById("butt").click();
        }
    });
    //載入首頁時同時連上userstatus檢視使用者狀態
    checkUser();
    let sign = document.getElementById("sign");
    function checkUser(){
        let userstatusUrl = "http://3.131.86.32:3000/api/user/userstatus/"
        fetch(userstatusUrl).then((res)=>res.json())
        .then((jsonData)=>{
            if(jsonData != null){
                //使用者已登入
                sign.remove();
                var newSign = document.createElement("p");
                newSign.id = "newsign";
                newSign.className = "item";
                newSign.textContent = "登出系統";
                let nav = document.getElementById("nav");
                nav.append(newSign);
                //登入狀態點擊預定行程，導入/booking:
                bookingschedule();
                //使用者點擊登出系統
                let signOut = document.getElementById("newsign");
                signOut.addEventListener("click" ,()=>{
                    let signoutUrl = "http://3.131.86.32:3000/api/user/signout/";
                    fetch(signoutUrl,{method:"DELETE", "Content-Type":"application/json"})
                    signOut.remove();
                    sign = document.createElement("p");
                    sign.id = "sign";
                    sign.className = "item";
                    sign.textContent = "登入/註冊";
                    nav.append(sign);
                    window.setTimeout(()=>{
                        location.reload();
                    },500);      

                });
            }else{
                //未登入點擊預定行程，跳出登入視窗
                let booking = document.getElementById("booking");
                let popupForm = document.querySelector(".popup_form");
                let mask = document.querySelector(".mask");
                let signinCancle = document.getElementById("signin_cancle") 
                booking.addEventListener("click" , ()=>{
                    popupForm.style.display = "block";
                    mask.style.display = "block";
                    cancleBox(signinCancle,popupForm);
                });
            
            }
        });
    }
//登入視窗部分:
    //test(操作1:點擊彈出登入框)
    let popupForm = document.querySelector(".popup_form");
    let mask = document.querySelector(".mask");
    let signinCancle = document.getElementById("signin_cancle") 
    sign.addEventListener("click" , ()=>{
        popupForm.style.display = "block";
        mask.style.display = "block";
        cancleBox(signinCancle,popupForm);
    });
    //(操作2:使用者登入)
    let signinForm = document.getElementById("signin_form");
    let signinResult = document.getElementById("signin_result");
    signinForm.addEventListener("submit",(e)=>{
        e.preventDefault();
        let signinUrl = "http://3.131.86.32:3000/api/user/signin/";
        let email = document.getElementById("signin_email").value;
        let password = document.getElementById("signin_password").value;
        let data = {
            "email":email,
            "password":password
        };
        fetch(signinUrl,{method:"PATCH",headers:{"Content-Type":"application/json"},
        body:JSON.stringify(data)}).then((res)=>res.json())
        .then((user)=>{
            let ok = user["ok"];
            if(ok == true){
                signinResult.innerHTML = "登入成功!!";
                window.setTimeout(()=>{
                    location.reload();
                },1000);
            }else{
                let message = user["message"];
                signinResult.innerHTML = message;
            }
        });
    });
    //(操作3:使用者尚未註冊，切換至註冊頁面) 
    let popupSignupForm = document.querySelector(".popup_form_sign_up");
    let signupCancle = document.querySelector(".signup_cancle");   
    signinResult.addEventListener("click",()=>{
        popupForm.style.display = "none";
        popupSignupForm.style.display = "block";
        cancleBox(signupCancle,popupSignupForm);
    });
    //(操作4:使用者註冊完畢送出)
    let signupForm = document.getElementById("signup_form");
    let signupUrl = "http://3.131.86.32:3000/api/user/signup/";
    let signupResult = document.getElementById("signup_result");
    signupForm.addEventListener("submit",(e)=>{
        e.preventDefault();
        let name = document.getElementById("signup_name").value;
        let email = document.getElementById("signup_email").value;
        let password = document.getElementById("signup_pw").value;
        let data = {
            "name":name,
            "email":email,
            "password":password
        };
        fetch(signupUrl,{method:"POST",headers:{"Content-Type":"application/json"}
        ,body:JSON.stringify(data)}).then((res)=>res.json())
        .then((user)=>{
            let ok = user["ok"];
            if(ok == true){
                signupResult.innerHTML = "註冊成功!!";
            }else{
                let message = user["message"];
                signupResult.innerHTML = message;
            }
        });
    });
    //(操作5:使用者返回登入)
    signupResult.addEventListener("click",()=>{
        popupSignupForm.style.display = "none";
        popupForm.style.display = "block";
    });
    // click cancle function(返回首頁函式)
    function cancleBox(p1,p2){
        p1.addEventListener("click" , function(){
            p2.style.display = "none";
            mask.style.display = "none";
        });
    }
}
//預定行程按鈕
function bookingschedule(){
    let booking = document.getElementById("booking");
    booking.addEventListener("click",()=>{
        location.href="http://3.131.86.32:3000/booking";
    });
}
//Debounce function(用於限制連續呼叫API)
let debounce=(fn,delay)=>{
    let timer;
    return function(){
        clearTimeout(timer)
        timer = setTimeout(()=>{
            fn()
        },delay)
    }
}

let incrementCount = ()=>{
    if(window.scrollY+window.innerHeight+30 >= document.documentElement.scrollHeight){
    //如果keyword有被搜尋則不繼續對page提出發送
        if(keyword == null){
            if (nextPage<=26){
                if(nextPage>=1){
                    getPageData(nextPage);
                }else{
                    getPageData(nextPage);
                }
            }
        }else{
            //當使用者關鍵字搜尋滑到底，停止載入
            if(kynextPage!="null"){
                kypage+=1;
                keywordSearch();
            }
        }
    }
    // console.log(document.documentElement.scrollHeight);
    // console.log(window.scrollY+window.innerHeight);
}

incrementCount = debounce(incrementCount,200);
window.addEventListener("scroll",incrementCount);