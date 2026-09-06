document.addEventListener(
    "DOMContentLoaded",
    function () {

        const checkIn =
            document.querySelector(
                'input[name="check_in"]'
            );

        const checkOut =
            document.querySelector(
                'input[name="check_out"]'
            );


        if (!checkIn || !checkOut) {
            return;
        }


        const today =
            new Date()
                .toISOString()
                .split("T")[0];


        checkIn.min = today;


        checkIn.addEventListener(
            "change",
            function () {

                if (!checkIn.value) {
                    return;
                }


                const selectedDate =
                    new Date(checkIn.value);


                selectedDate.setDate(
                    selectedDate.getDate() + 1
                );


                const minimumCheckout =
                    selectedDate
                        .toISOString()
                        .split("T")[0];


                checkOut.min =
                    minimumCheckout;


                if (
                    checkOut.value &&
                    checkOut.value <= checkIn.value
                ) {

                    checkOut.value = "";

                }

            }
        );

    }
);