
async function submit () {
    const batch = [];
    for (const input of document.getElementsByClassName("ip-input")) {
        if (input.value.length !== 0)
            batch.push(input.value);
    }
    const resp = await fetch("/api/batch", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        body: JSON.stringify(batch)
    });


    const data = await resp.json();
    const id = data["id"];

    window.location.href = `/result/${id}`;

}