/* =========================================================
   INTELLIVISION - MAIN FRONTEND CONTROLLER
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* -----------------------------------------------------
       STATE
    ----------------------------------------------------- */

    let mediaRecorder = null;
    let audioChunks = [];
    let recordingInterval = null;
    let recordingSeconds = 0;

    let currentAudioPath = null;
    let currentComplaintId = null;
    let currentFirId = null;
    let currentFIR = null;


    /* -----------------------------------------------------
       DOM REFERENCES
    ----------------------------------------------------- */

    const recordButton = document.getElementById("recordButton");
    const stopButton = document.getElementById("stopButton");
    const recordingStatus = document.getElementById("recordingStatus");
    const recordingTimer = document.getElementById("recordingTimer");

    const audioPreview = document.getElementById("audioPreview");
    const audioPlayer = document.getElementById("audioPlayer");

    const transcribeButton = document.getElementById("transcribeButton");
    const transcriptionSection =
        document.getElementById("transcriptionSection");

    const transcription =
        document.getElementById("transcription");

    const detectedLanguage =
        document.getElementById("detectedLanguage");

    const generateButton =
        document.getElementById("generateButton");

    const generationStatus =
        document.getElementById("generationStatus");

    const firSection =
        document.getElementById("firSection");

    const approveButton =
        document.getElementById("approveButton");

    const rejectButton =
        document.getElementById("rejectButton");

    const reviewStatus =
        document.getElementById("reviewStatus");

    const finalSection =
        document.getElementById("finalSection");

    const printButton =
        document.getElementById("printButton");


    /* -----------------------------------------------------
       UTILITY FUNCTIONS
    ----------------------------------------------------- */

    function showElement(element) {
        if (element) {
            element.hidden = false;
            element.style.display = "";
        }
    }

    function hideElement(element) {
        if (element) {
            element.hidden = true;
        }
    }

    function setStatus(element, message, type = "") {
        if (!element) return;

        element.textContent = message;

        element.classList.remove(
            "success",
            "error",
            "loading"
        );

        if (type) {
            element.classList.add(type);
        }
    }

    function formatDateTime(value) {
        if (!value) return "";

        try {
            const date = new Date(value);

            if (Number.isNaN(date.getTime())) {
                return value;
            }

            return date.toLocaleString("en-IN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                hour12: false
            });
        } catch {
            return value;
        }
    }


    /* -----------------------------------------------------
       WORKFLOW STEP HELPERS
    ----------------------------------------------------- */

    function activateStep(stepNumber) {

        document.querySelectorAll(".iv-step").forEach(step => {
            const number =
                step.querySelector(".iv-step-number");

            if (!number) return;

            const stepValue =
                parseInt(number.textContent.trim());

            step.classList.remove("active");

            if (stepValue < stepNumber) {
                step.classList.add("completed");
            }

            if (stepValue === stepNumber) {
                step.classList.add("active");
            }
        });
    }


    /* -----------------------------------------------------
       RECORDING TIMER
    ----------------------------------------------------- */

    function resetTimer() {
        recordingSeconds = 0;

        if (recordingTimer) {
            recordingTimer.textContent = "00:00";
        }
    }

    function startTimer() {

        resetTimer();

        recordingInterval =
            setInterval(() => {

                recordingSeconds++;

                const minutes =
                    Math.floor(recordingSeconds / 60);

                const seconds =
                    recordingSeconds % 60;

                if (recordingTimer) {
                    recordingTimer.textContent =
                        `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
                }

            }, 1000);
    }

    function stopTimer() {

        if (recordingInterval) {
            clearInterval(recordingInterval);
            recordingInterval = null;
        }
    }


    /* -----------------------------------------------------
       START RECORDING
    ----------------------------------------------------- */

    if (recordButton) {

        recordButton.addEventListener("click", async () => {

            try {

                if (!navigator.mediaDevices ||
                    !navigator.mediaDevices.getUserMedia) {

                    setStatus(
                        recordingStatus,
                        "Audio recording is not supported by this browser.",
                        "error"
                    );

                    return;
                }

                const stream =
                    await navigator.mediaDevices.getUserMedia({
                        audio: true
                    });

                audioChunks = [];

                mediaRecorder =
                    new MediaRecorder(stream);

                mediaRecorder.addEventListener(
                    "dataavailable",
                    event => {

                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }

                    }
                );

                mediaRecorder.addEventListener(
                    "stop",
                    async () => {

                        stream.getTracks().forEach(
                            track => track.stop()
                        );

                        const audioBlob =
                            new Blob(audioChunks, {
                                type: "audio/webm"
                            });

                        await uploadRecording(audioBlob);
                    }
                );

                mediaRecorder.start();

                recordButton.disabled = true;

                if (stopButton) {
                    stopButton.disabled = false;
                }

                setStatus(
                    recordingStatus,
                    "Recording complaint...",
                    "loading"
                );

                startTimer();

            } catch (error) {

                console.error(
                    "Recording error:",
                    error
                );

                setStatus(
                    recordingStatus,
                    "Unable to access microphone.",
                    "error"
                );
            }
        });
    }


    /* -----------------------------------------------------
       STOP RECORDING
    ----------------------------------------------------- */

    if (stopButton) {

        stopButton.addEventListener("click", () => {

            if (!mediaRecorder) return;

            if (mediaRecorder.state === "recording") {
                mediaRecorder.stop();
            }

            stopTimer();

            stopButton.disabled = true;

            if (recordButton) {
                recordButton.disabled = false;
            }

            setStatus(
                recordingStatus,
                "Recording stopped. Preparing audio..."
            );
        });
    }


    /* -----------------------------------------------------
       UPLOAD RECORDING
    ----------------------------------------------------- */

    async function uploadRecording(audioBlob) {

        try {

            setStatus(
                recordingStatus,
                "Uploading recorded complaint...",
                "loading"
            );

            const formData =
                new FormData();

            formData.append(
                "audio",
                audioBlob,
                "complaint.webm"
            );

            const response =
                await fetch(
                    "/transcription/transcribe",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            if (!response.ok || !data.success) {

                throw new Error(
                    data.error ||
                    "Failed to process audio."
                );
            }

            currentAudioPath =
                data.audio_path || null;

            currentComplaintId =
                data.complaint_id || null;

            if (audioPreview) {
                showElement(audioPreview);
            }

            if (audioPlayer &&
                data.audio_url) {

                audioPlayer.src =
                    data.audio_url;

                audioPlayer.load();
            }

            setStatus(
                recordingStatus,
                "Recording ready. Click Transcribe."
            );

            if (transcribeButton) {
                transcribeButton.disabled = false;
            }

        } catch (error) {

            console.error(
                "Upload error:",
                error
            );

            setStatus(
                recordingStatus,
                error.message ||
                "Unable to upload recording.",
                "error"
            );
        }
    }


    /* -----------------------------------------------------
       TRANSCRIBE
    ----------------------------------------------------- */

    if (transcribeButton) {

        transcribeButton.addEventListener(
            "click",
            async () => {

                try {

                    if (!currentAudioPath) {

                        setStatus(
                            recordingStatus,
                            "Please record a complaint first.",
                            "error"
                        );

                        return;
                    }

                    transcribeButton.disabled = true;

                    setStatus(
                        recordingStatus,
                        "Whisper is transcribing the complaint...",
                        "loading"
                    );

                    const response =
                        await fetch(
                            "/transcription/transcribe",
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },
                                body: JSON.stringify({
                                    audio_path:
                                        currentAudioPath,
                                    complaint_id:
                                        currentComplaintId
                                })
                            }
                        );

                    const data =
                        await response.json();

                    /*
                     * Some backend versions return the
                     * transcription from the upload call.
                     * Support both response formats.
                     */

                    if (!response.ok ||
                        data.success === false) {

                        throw new Error(
                            data.error ||
                            "Transcription failed."
                        );
                    }

                    if (data.complaint_id) {
                        currentComplaintId =
                            data.complaint_id;
                    }

                    if (data.transcription) {

                        if (transcription) {
                            transcription.value =
                                data.transcription;
                        }

                    }

                    if (data.detected_language) {

                        if (detectedLanguage) {
                            detectedLanguage.textContent =
                                data.detected_language;
                        }
                    }

                    showElement(transcriptionSection);

                    activateStep(2);

                    setStatus(
                        recordingStatus,
                        "Transcription completed.",
                        "success"
                    );

                } catch (error) {

                    console.error(
                        "Transcription error:",
                        error
                    );

                    setStatus(
                        recordingStatus,
                        error.message ||
                        "Unable to transcribe complaint.",
                        "error"
                    );

                    transcribeButton.disabled = false;
                }
            }
        );
    }


    /* -----------------------------------------------------
       GENERATE FIR
    ----------------------------------------------------- */

    if (generateButton) {

        generateButton.addEventListener(
            "click",
            async () => {

                try {

                    const complaintText =
                        transcription
                            ? transcription.value.trim()
                            : "";

                    if (!complaintText) {

                        setStatus(
                            generationStatus,
                            "Please provide complaint text first.",
                            "error"
                        );

                        return;
                    }

                    generateButton.disabled = true;

                    setStatus(
                        generationStatus,
                        "Investigation Agent is analyzing the complaint and generating the FIR draft...",
                        "loading"
                    );

                    const response =
                        await fetch(
                            "/fir/generate",
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },
                                body: JSON.stringify({
                                    complaint_id:
                                        currentComplaintId,
                                    transcription:
                                        complaintText
                                })
                            }
                        );

                    const data =
                        await response.json();

                    if (!response.ok ||
                        !data.success) {

                        throw new Error(
                            data.error ||
                            "FIR generation failed."
                        );
                    }

                    currentFirId =
                        data.fir_id;

                    currentFIR =
                        data;

                    /*
                     * The backend may return the full FIR
                     * data directly or the page may already
                     * contain the generated fields.
                     */

                    populateFIR(data);

                    showElement(firSection);

                    activateStep(3);

                    setStatus(
                        generationStatus,
                        "FIR draft generated successfully.",
                        "success"
                    );

                    window.scrollTo({
                        top:
                            firSection
                                ? firSection.offsetTop - 30
                                : document.body.scrollHeight,
                        behavior: "smooth"
                    });

                } catch (error) {

                    console.error(
                        "FIR generation error:",
                        error
                    );

                    setStatus(
                        generationStatus,
                        error.message ||
                        "Unable to generate FIR draft.",
                        "error"
                    );

                    generateButton.disabled = false;
                }
            }
        );
    }


    /* -----------------------------------------------------
       FIR FIELD POPULATION
    ----------------------------------------------------- */

    function setField(
        selector,
        value,
        allowEmpty = true
    ) {

        const element =
            document.querySelector(selector);

        if (!element) return;

        if (
            value !== undefined &&
            value !== null &&
            String(value).trim() !== ""
        ) {

            if (
                element.tagName === "INPUT" ||
                element.tagName === "TEXTAREA" ||
                element.tagName === "SELECT"
            ) {
                element.value = value;
            } else {
                element.textContent = value;
            }

        } else if (allowEmpty) {

            if (
                element.tagName === "INPUT" ||
                element.tagName === "TEXTAREA" ||
                element.tagName === "SELECT"
            ) {
                element.value = "";
            } else {
                element.textContent = "";
            }
        }
    }


    function setSystemField(selector, value) {

        const element =
            document.querySelector(selector);

        if (!element) return;

        const finalValue =
            value === undefined ||
            value === null
                ? ""
                : value;

        if (
            element.tagName === "INPUT" ||
            element.tagName === "TEXTAREA" ||
            element.tagName === "SELECT"
        ) {
            element.value = finalValue;
        } else {
            element.textContent = finalValue;
        }

        element.classList.add("system-field");
    }


    function populateFIR(data) {

        /*
         * This function intentionally does not invent
         * values. Empty values remain empty.
         */

        const fir =
            data.fir ||
            data.fir_data ||
            data;

        if (!fir) return;

        currentFIR = fir;

        /* System-controlled fields */

        setSystemField(
            "#firNumber",
            fir.fir_number ||
            fir.proposed_fir_number ||
            ""
        );

        setSystemField(
            "#policeStation",
            fir.police_station || ""
        );

        setSystemField(
            "#district",
            fir.district || ""
        );

        setSystemField(
            "#firYear",
            fir.year || ""
        );

        setSystemField(
            "#informationReceivedDatetime",
            formatDateTime(
                fir.information_received_datetime
            )
        );

        setSystemField(
            "#firDateTime",
            formatDateTime(
                fir.fir_date_time
            )
        );


        /* AI-assisted / officer-editable fields */

        setField(
            "#complainantName",
            fir.complainant_name
        );

        setField(
            "#fatherHusbandName",
            fir.father_husband_name
        );

        setField(
            "#dateOfBirth",
            fir.date_of_birth
        );

        setField(
            "#nationality",
            fir.nationality
        );

        setField(
            "#uidNumber",
            fir.uid_number
        );

        setField(
            "#passportNumber",
            fir.passport_number
        );

        setField(
            "#otherIdDetails",
            fir.other_id_details
        );

        setField(
            "#occupation",
            fir.occupation
        );

        setField(
            "#complainantAddress",
            fir.complainant_address
        );

        setField(
            "#phoneNumber",
            fir.phone_number
        );

        setField(
            "#mobileNumber",
            fir.mobile_number
        );

        setField(
            "#occurrenceFrom",
            formatDateTime(
                fir.occurrence_from
            )
        );

        setField(
            "#occurrenceTo",
            formatDateTime(
                fir.occurrence_to
            )
        );

        setField(
            "#placeOfOccurrence",
            fir.place_of_occurrence
        );

        setField(
            "#accusedDetails",
            fir.accused_details
        );

        setField(
            "#reasonForDelay",
            fir.reason_for_delay
        );

        setField(
            "#propertyDetails",
            fir.property_details
        );

        setField(
            "#totalPropertyValue",
            fir.total_property_value
        );

        setField(
            "#firstInformationContents",
            fir.first_information_contents
        );

        setField(
            "#actionTaken",
            fir.action_taken
        );

        setField(
            "#crimeCategory",
            fir.crime_category
        );

        setField(
            "#act",
            fir.act
        );

        setField(
            "#sections",
            fir.sections
        );

        /*
         * Alternative IDs used by some versions
         * of the FIR HTML.
         */

        setField(
            "#firNarrative",
            fir.first_information_contents
        );

        setField(
            "#fir-narrative",
            fir.first_information_contents
        );


        /* Missing information */

        const missing =
            data.missing_information ||
            fir.missing_information ||
            [];

        const missingBox =
            document.getElementById(
                "missingInformationBox"
            );

        const missingList =
            document.getElementById(
                "missingInformationList"
            );

        if (missingList) {

            missingList.innerHTML = "";

            if (Array.isArray(missing) &&
                missing.length > 0) {

                missing.forEach(item => {

                    const li =
                        document.createElement("li");

                    li.textContent = item;

                    missingList.appendChild(li);
                });

                if (missingBox) {
                    showElement(missingBox);
                }

            } else {

                if (missingBox) {
                    hideElement(missingBox);
                }
            }
        }
    }


    /* -----------------------------------------------------
       APPROVE FIR
    ----------------------------------------------------- */

    if (approveButton) {

        approveButton.addEventListener(
            "click",
            async () => {

                try {

                    if (!currentFirId) {

                        setStatus(
                            reviewStatus,
                            "FIR draft ID is missing.",
                            "error"
                        );

                        return;
                    }

                    approveButton.disabled = true;

                    if (rejectButton) {
                        rejectButton.disabled = true;
                    }

                    setStatus(
                        reviewStatus,
                        "Saving officer edits and approving FIR...",
                        "loading"
                    );

                    const editedFields =
                        collectEditableFields();

                    const response =
                        await fetch(
                            `/fir/approve/${currentFirId}`,
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },
                                body: JSON.stringify(
                                    editedFields
                                )
                            }
                        );

                    const data =
                        await response.json();

                    if (!response.ok ||
                        !data.success) {

                        throw new Error(
                            data.error ||
                            "FIR approval failed."
                        );
                    }

                    setStatus(
                        reviewStatus,
                        `FIR approved successfully. FIR Number: ${data.fir_number || ""}`,
                        "success"
                    );

                    activateStep(4);

                    showElement(finalSection);

                    populateFinalSection(data);

                    window.scrollTo({
                        top:
                            finalSection
                                ? finalSection.offsetTop - 30
                                : document.body.scrollHeight,
                        behavior: "smooth"
                    });

                } catch (error) {

                    console.error(
                        "Approval error:",
                        error
                    );

                    setStatus(
                        reviewStatus,
                        error.message ||
                        "Unable to approve FIR.",
                        "error"
                    );

                    approveButton.disabled = false;

                    if (rejectButton) {
                        rejectButton.disabled = false;
                    }
                }
            }
        );
    }


    /* -----------------------------------------------------
       COLLECT OFFICER EDITS
    ----------------------------------------------------- */

    function collectEditableFields() {

        const fields = {};

        const selectors = [
            "#complainantName",
            "#fatherHusbandName",
            "#dateOfBirth",
            "#nationality",
            "#uidNumber",
            "#passportNumber",
            "#otherIdDetails",
            "#occupation",
            "#complainantAddress",
            "#phoneNumber",
            "#mobileNumber",
            "#occurrenceFrom",
            "#occurrenceTo",
            "#placeOfOccurrence",
            "#accusedDetails",
            "#reasonForDelay",
            "#propertyDetails",
            "#totalPropertyValue",
            "#firstInformationContents",
            "#actionTaken",
            "#crimeCategory",
            "#act",
            "#sections",
            "#firNarrative",
            "#fir-narrative"
        ];

        selectors.forEach(selector => {

            const element =
                document.querySelector(selector);

            if (!element) return;

            const key =
                selector.replace("#", "");

            fields[key] =
                element.value !== undefined
                    ? element.value
                    : element.textContent.trim();
        });

        return fields;
    }


    /* -----------------------------------------------------
       REJECT FIR
    ----------------------------------------------------- */

    if (rejectButton) {

        rejectButton.addEventListener(
            "click",
            async () => {

                try {

                    if (!currentFirId) {

                        setStatus(
                            reviewStatus,
                            "FIR draft ID is missing.",
                            "error"
                        );

                        return;
                    }

                    const confirmed =
                        window.confirm(
                            "Reject this FIR draft and start a new complaint?"
                        );

                    if (!confirmed) {
                        return;
                    }

                    rejectButton.disabled = true;

                    if (approveButton) {
                        approveButton.disabled = true;
                    }

                    setStatus(
                        reviewStatus,
                        "Rejecting FIR draft...",
                        "loading"
                    );

                    const response =
                        await fetch(
                            `/fir/reject/${currentFirId}`,
                            {
                                method: "POST"
                            }
                        );

                    const data =
                        await response.json();

                    if (!response.ok ||
                        !data.success) {

                        throw new Error(
                            data.error ||
                            "Unable to reject FIR."
                        );
                    }

                    setStatus(
                        reviewStatus,
                        "Draft rejected. Please record a new complaint."
                    );

                    /*
                     * Reset the workflow.
                     * We deliberately do NOT regenerate
                     * the same complaint.
                     */

                    resetForNewComplaint();

                } catch (error) {

                    console.error(
                        "Reject error:",
                        error
                    );

                    setStatus(
                        reviewStatus,
                        error.message ||
                        "Unable to reject FIR.",
                        "error"
                    );

                    rejectButton.disabled = false;

                    if (approveButton) {
                        approveButton.disabled = false;
                    }
                }
            }
        );
    }


    /* -----------------------------------------------------
       RESET FOR NEW COMPLAINT
    ----------------------------------------------------- */

    function resetForNewComplaint() {

        currentAudioPath = null;
        currentComplaintId = null;
        currentFirId = null;
        currentFIR = null;

        if (transcription) {
            transcription.value = "";
        }

        if (audioPlayer) {
            audioPlayer.removeAttribute("src");
            audioPlayer.load();
        }

        hideElement(audioPreview);
        hideElement(transcriptionSection);
        hideElement(firSection);
        hideElement(finalSection);

        if (transcribeButton) {
            transcribeButton.disabled = true;
        }

        if (generateButton) {
            generateButton.disabled = false;
        }

        if (recordButton) {
            recordButton.disabled = false;
        }

        if (stopButton) {
            stopButton.disabled = true;
        }

        resetTimer();

        activateStep(1);

        setStatus(
            recordingStatus,
            "Ready for a new complaint."
        );

        if (generationStatus) {
            generationStatus.textContent = "";
        }

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }


    /* -----------------------------------------------------
       FINAL SECTION
    ----------------------------------------------------- */

    function populateFinalSection(data) {

        const firNumber =
            data.fir_number ||
            "";

        const finalFirNumber =
            document.getElementById(
                "finalFirNumber"
            );

        if (finalFirNumber) {
            finalFirNumber.textContent =
                firNumber;
        }

        const finalStatus =
            document.getElementById(
                "finalStatus"
            );

        if (finalStatus) {
            finalStatus.textContent =
                "APPROVED";
        }

        const finalDate =
            document.getElementById(
                "finalDate"
            );

        if (finalDate &&
            data.approval_datetime) {

            finalDate.textContent =
                formatDateTime(
                    data.approval_datetime
                );
        }
    }


    /* -----------------------------------------------------
       PRINT
    ----------------------------------------------------- */

    if (printButton) {

        printButton.addEventListener(
            "click",
            () => {
                window.print();
            }
        );
    }


    /* -----------------------------------------------------
       INITIAL STATE
    ----------------------------------------------------- */

    hideElement(transcriptionSection);
    hideElement(firSection);
    hideElement(finalSection);

    if (stopButton) {
        stopButton.disabled = true;
    }

    if (transcribeButton) {
        transcribeButton.disabled = true;
    }

    activateStep(1);

});