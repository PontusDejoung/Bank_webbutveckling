pageNR = 2;
hasNext = true;


function fetchMoreTransactions() {
    url = "/api/{{ account.Id }}/transaction?page=" + pageNR;
    fetch(url)
        .then((response)=>response.json())
        .then((json)=>{
            hasNext = json[1]
            pageNR = pageNR + 1;
            json[0].foreach(tableElement);
            if (hasNext == false){
                document.getElementById("moreTrans").style.visibility = "hidden";
                document.getElementById("transaction").innerHTML = 'No more transactions to show';
            }
        });
}

function tableElement(element) {
    document.querySelector('#table-post tbody').innerHTML +=
        `<tr>
            <td scope="row">${element.Id}</td>
            <td>${element.Date}</td>
            <td>${element.Type}</td>
            <td>${element.Operation}</td>
            <td>${element.Amount}</td>
            <td>${element.AccountId}</td>
                
        </tr>`;
        }

        $(document).ready(function () {
            var trigger = $('.hamburger'),
                overlay = $('.overlay'),
               isClosed = false;
          
              trigger.click(function () {
                hamburger_cross();      
              });
          
              function hamburger_cross() {
          
                if (isClosed == true) {          
                  overlay.hide();
                  trigger.removeClass('is-open');
                  trigger.addClass('is-closed');
                  isClosed = false;
                } else {   
                  overlay.show();
                  trigger.removeClass('is-closed');
                  trigger.addClass('is-open');
                  isClosed = true;
                }
            }
            
            $('[data-toggle="offcanvas"]').click(function () {
                  $('#wrapper').toggleClass('toggled');
            });  
          });