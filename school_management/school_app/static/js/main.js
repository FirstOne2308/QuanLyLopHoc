const menu = document.querySelector('#sidebar');
const menuLinks = document.querySelector('.sidebar');
const main = document.querySelector('.list-container');

// Display Mobile Menu
const mobileMenu = () => {
  menu.classList.toggle('is-active');
  menuLinks.classList.toggle('active');
  main.classList.toggle('active');
}

menu.addEventListener('click', mobileMenu)



const dropdownMenu = document.querySelector(".dropdown-menu");
const dropdownButton = document.querySelector(".dropdown-button");

if (dropdownButton) {
    dropdownButton.addEventListener("click", () => {
    dropdownMenu.classList.toggle('show');
  });
}



const sidebarLink = document.querySelector(".sidebar-link");

const sidebarLinkSelect = () => {
  sidebarLink.classList.toggle('is-selected');
  // console.assert('hi');
}

sidebarLink.addEventListener('click', sidebarLinkSelect);


const mainRpSj = document.querySelector(".main-rp-sj");
const mainRpTerm = document.querySelector(".main-rp-term");


const tapTerm = document.querySelector(".item-term");
const tapSubject = document.querySelector(".item-subject");

tapTerm.addEventListener("click", () => {
  mainRpTerm.classList.remove("notactive");
  mainRpSj.classList.remove("active");
  tapTerm.classList.remove("notactive");
  tapSubject.classList.remove("active");
  
  mainRpTerm.classList.add("active");
  mainRpSj.classList.add("notactive");
  tapTerm.classList.add("active");
  tapSubject.classList.add("notactive");
});

tapSubject.addEventListener("click", () => {

  mainRpTerm.classList.remove("active");
  mainRpSj.classList.remove("notactive");
  tapSubject.classList.remove("notactive");
  tapTerm.classList.remove("active");

  mainRpTerm.classList.add("notactive");
  mainRpSj.classList.add("active");
  tapSubject.classList.add("active");
  tapTerm.classList.add("notactive");
})


