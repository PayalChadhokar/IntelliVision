document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // GLOBAL VARIABLES
    // =========================================================

    let mediaRecorder = null;
    let audioChunks = [];
    let recordedAudioBlob = null;
    let currentAudioPath = null;
    let currentComplaintId = null;
    let currentFirId = null;
    let currentFIR = null;

    let recordingTimerInterval = null;
    let recordingSeconds = 0;
    let isRecording = false;


    // =========================================================
    // DOM ELEMENTS
    // =========================================================

    const recordButton = document.getElementById("recordButton");
    const stopButton = document.getElementById("stopButton");

    const recordingStatus =
        document.getElementById("recordingStatus");

    const recordingTimer =
        document.getElementById("recordingTimer");

    const recordingDuration =
        document.getElementById("recordingDuration");

    const audioPreview =
        document.getElementById("audioPreview");

    const audioPlayer =
        document.getElementById("audioPlayer");

    const transcribeButton =
        document.getElementById("transcribeButton");

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

    const finalSection =
        document.getElementById("finalSection");

    const reviewStatus =
        document.getElementById("reviewStatus");

    const printButton =
        document.getElementById("printButton");


    // =========================================================
    // HELPER FUNCTIONS
    // =========================================================

    function setText(element, value) {
        if (element) {
            element.textContent = value ?? "";
        }
    }


    function show(element) {
        if (element) {
            element.style.display = "";
        }
    }


    function hide(element) {
        if (element) {
            element.style.display = "none";
        }
    }


    function formatTime(seconds) {

        const minutes =
            Math.floor(seconds / 60);

        const secs =
            seconds % 60;

        return (
            String(minutes).padStart(2, "0") +
            ":" +
            String(secs).padStart(2, "0")
        );
    }


    // =========================================================
    // RECORDING TIMER
    // =========================================================

    function startRecordingTimer() {

        recordingSeconds = 0;

        setText(
            recordingTimer,
            "00:00"
        );

        setText(
            recordingDuration,
            "00:00"
        );

        clearInterval(
            recordingTimerInterval
        );

        recordingTimerInterval =
            setInterval(function () {

                recordingSeconds++;

                const formatted =
                    formatTime(recordingSeconds);

                setText(
                    recordingTimer,
                    formatted
                );

                setText(
                    recordingDuration,
                    formatted
                );

            }, 1000);
    }


    function stopRecordingTimer() {

        clearInterval(
            recordingTimerInterval
        );

        recordingTimerInterval = null;
    }


    // =========================================================
    // BUTTON EVENTS
    // =========================================================

    if (recordButton) {

        recordButton.disabled = false;

        recordButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();

                if (isRecording) {
                    return;
                }

                await startRecording();

            }
        );
    }


    if (stopButton) {

        stopButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                if (!isRecording) {
                    return;
                }

                stopRecording();

            }
        );
    }


    // =========================================================
    // START RECORDING
    // =========================================================

    async function startRecording() {

        console.log(
            "IntelliVision: Start Recording clicked."
        );

        try {

            setText(
                recordingStatus,
                "Requesting microphone access..."
            );


            // -------------------------------------------------
            // Browser microphone support
            // -------------------------------------------------

            if (
                !navigator.mediaDevices ||
                !navigator.mediaDevices.getUserMedia
            ) {

                throw new Error(
                    "Microphone access is not supported by this browser. Please use Chrome or Edge."
                );
            }


            // -------------------------------------------------
            // Secure context check
            // -------------------------------------------------

            if (
                !window.isSecureContext &&
                location.hostname !== "localhost" &&
                location.hostname !== "127.0.0.1"
            ) {

                throw new Error(
                    "Microphone access requires HTTPS or localhost. Please open http://127.0.0.1:5000."
                );
            }


            // -------------------------------------------------
            // MediaRecorder support
            // -------------------------------------------------

            if (
                typeof MediaRecorder === "undefined"
            ) {

                throw new Error(
                    "This browser does not support audio recording. Please use the latest Chrome or Edge."
                );
            }


            // -------------------------------------------------
            // Request microphone
            // -------------------------------------------------

            const stream =
                await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        channelCount: 1
                    }
                });


            console.log(
                "IntelliVision: Microphone permission granted."
            );


            audioChunks = [];

            recordedAudioBlob = null;

            currentAudioPath = null;


            // -------------------------------------------------
            // Find supported audio format
            // -------------------------------------------------

            const supportedTypes = [

                "audio/webm;codecs=opus",

                "audio/webm",

                "audio/ogg;codecs=opus"

            ];


            let mimeType = "";


            for (
                const type of supportedTypes
            ) {

                if (
                    MediaRecorder.isTypeSupported(type)
                ) {

                    mimeType = type;

                    break;
                }
            }


            console.log(
                "IntelliVision: Selected audio format:",
                mimeType || "browser default"
            );


            // -------------------------------------------------
            // Create MediaRecorder
            // -------------------------------------------------

            mediaRecorder =
                mimeType
                    ? new MediaRecorder(
                        stream,
                        {
                            mimeType: mimeType
                        }
                    )
                    : new MediaRecorder(stream);


            // -------------------------------------------------
            // Audio chunks
            // -------------------------------------------------

            mediaRecorder.ondataavailable =
                function (event) {

                    if (
                        event.data &&
                        event.data.size > 0
                    ) {

                        audioChunks.push(
                            event.data
                        );

                    }
                };


            // -------------------------------------------------
            // Recording started
            // -------------------------------------------------

            mediaRecorder.onstart =
                function () {

                    console.log(
                        "IntelliVision: MediaRecorder started."
                    );

                    isRecording = true;


                    if (recordButton) {

                        recordButton.disabled = true;

                        recordButton.textContent =
                            "🔴 Recording...";

                    }


                    if (stopButton) {

                        stopButton.disabled = false;

                    }


                    setText(
                        recordingStatus,
                        "Recording complainant statement..."
                    );


                    if (recordingStatus) {

                        recordingStatus.className =
                            "iv-recording-status recording";

                    }


                    startRecordingTimer();
                };


            // -------------------------------------------------
            // Recording stopped
            // -------------------------------------------------

            mediaRecorder.onstop =
                async function () {

                    console.log(
                        "IntelliVision: MediaRecorder stopped."
                    );

                    isRecording = false;

                    stopRecordingTimer();


                    // Stop microphone
                    stream
                        .getTracks()
                        .forEach(
                            function (track) {
                                track.stop();
                            }
                        );


                    await new Promise(
                        function (resolve) {

                            setTimeout(
                                resolve,
                                100
                            );

                        }
                    );


                    await prepareRecordedAudio();
                };


            // -------------------------------------------------
            // Recorder error
            // -------------------------------------------------

            mediaRecorder.onerror =
                function (event) {

                    console.error(
                        "IntelliVision MediaRecorder error:",
                        event
                    );

                    isRecording = false;

                    stopRecordingTimer();

                    setText(
                        recordingStatus,
                        "Recording error occurred."
                    );

                    if (recordingStatus) {

                        recordingStatus.className =
                            "iv-recording-status error";

                    }

                    resetRecordingUI();
                };


            // -------------------------------------------------
            // START
            // -------------------------------------------------

            mediaRecorder.start(250);


            console.log(
                "IntelliVision: Recording started successfully."
            );

        }
        catch (error) {

            console.error(
                "IntelliVision microphone error:",
                error
            );


            isRecording = false;

            stopRecordingTimer();


            setText(
                recordingStatus,
                "Unable to access microphone."
            );


            if (recordingStatus) {

                recordingStatus.className =
                    "iv-recording-status error";
            }


            alert(
                error.message ||
                "Unable to access the microphone. Please allow microphone permission."
            );
        }
    }


    // =========================================================
    // STOP RECORDING
    // =========================================================

    function stopRecording() {

        console.log(
            "IntelliVision: Stopping recording..."
        );


        if (
            mediaRecorder &&
            mediaRecorder.state !== "inactive"
        ) {

            mediaRecorder.stop();


            if (stopButton) {

                stopButton.disabled = true;

            }


            setText(
                recordingStatus,
                "Processing recording..."
            );
        }
    }


    // =========================================================
    // PREPARE AUDIO
    // =========================================================

    async function prepareRecordedAudio() {

        console.log(
            "Preparing audio chunks:",
            audioChunks.length
        );


        if (!audioChunks.length) {

            setText(
                recordingStatus,
                "No audio was recorded."
            );


            resetRecordingUI();

            return;
        }


        // -----------------------------------------------------
        // Create audio blob
        // -----------------------------------------------------

        let mimeType =
            "audio/webm";


        if (
            audioChunks[0] &&
            audioChunks[0].type
        ) {

            mimeType =
                audioChunks[0].type;
        }


        recordedAudioBlob =
            new Blob(
                audioChunks,
                {
                    type: mimeType
                }
            );


        console.log(
            "IntelliVision: Audio size:",
            recordedAudioBlob.size
        );


        if (
            recordedAudioBlob.size === 0
        ) {

            alert(
                "The recorded audio is empty. Please record again."
            );


            resetRecordingUI();

            return;
        }


        // -----------------------------------------------------
        // Local audio preview
        // -----------------------------------------------------

        const audioURL =
            URL.createObjectURL(
                recordedAudioBlob
            );


        if (audioPlayer) {

            audioPlayer.src =
                audioURL;

            audioPlayer.controls =
                true;

            audioPlayer.load();
        }


        if (audioPreview) {

            audioPreview.style.display =
                "";
        }


        // -----------------------------------------------------
        // Enable transcription
        // -----------------------------------------------------

        if (transcribeButton) {

            transcribeButton.disabled =
                false;
        }


        setText(
            recordingStatus,
            "Recording ready. Click Transcribe."
        );


        if (recordingStatus) {

            recordingStatus.className =
                "iv-recording-status success";
        }


        if (recordButton) {

            recordButton.disabled =
                false;

            recordButton.textContent =
                "🎤 Record Again";
        }


        console.log(
            "IntelliVision: Audio prepared successfully."
        );
    }


    // =========================================================
    // RESET RECORDING UI
    // =========================================================

    function resetRecordingUI() {

        isRecording = false;

        audioChunks = [];

        recordedAudioBlob = null;

        currentAudioPath = null;

        stopRecordingTimer();


        if (recordButton) {

            recordButton.disabled =
                false;

            recordButton.textContent =
                "🎤 Start Recording";
        }


        if (stopButton) {

            stopButton.disabled =
                true;
        }


        setText(
            recordingStatus,
            "Ready to record"
        );


        setText(
            recordingTimer,
            "00:00"
        );


        setText(
            recordingDuration,
            "00:00"
        );
    }


    // =========================================================
    // TRANSCRIBE AUDIO
    // =========================================================

    if (transcribeButton) {

        transcribeButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                if (!recordedAudioBlob) {

                    alert(
                        "Please record your complaint first."
                    );

                    return;
                }


                transcribeButton.disabled =
                    true;

                transcribeButton.textContent =
                    "Transcribing...";


                setText(
                    recordingStatus,
                    "Converting speech to text..."
                );


                try {

                    const formData =
                        new FormData();


                    formData.append(
                        "audio",
                        recordedAudioBlob,
                        "complaint.webm"
                    );


                    console.log(
                        "Uploading audio for transcription..."
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


                    console.log(
                        "Transcription response:",
                        data
                    );


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            data.message ||
                            "Transcription failed."
                        );
                    }


                    if (
                        data.success === false
                    ) {

                        throw new Error(
                            data.error ||
                            "Transcription failed."
                        );
                    }


                    // -------------------------------------------------
                    // Save complaint information
                    // -------------------------------------------------

                    currentComplaintId =
                        data.complaint_id ||
                        data.complaintId ||
                        null;


                    currentAudioPath =
                        data.audio_path ||
                        data.audioPath ||
                        null;


                    // -------------------------------------------------
                    // Display transcription
                    // -------------------------------------------------

                    const transcriptText =
                        data.transcription ||
                        data.text ||
                        "";


                    if (transcription) {

                        transcription.value =
                            transcriptText;
                    }


                    // -------------------------------------------------
                    // Language
                    // -------------------------------------------------

                    const language =
                        data.language ||
                        data.detected_language ||
                        "";


                    const languageNames = {

                        en: "English",

                        hi: "Hindi",

                        mr: "Marathi"

                    };


                    const languageDisplay =
                        languageNames[language] ||
                        data.language_name ||
                        language ||
                        "Not detected";


                    setText(
                        detectedLanguage,
                        languageDisplay
                    );


                    // -------------------------------------------------
                    // Show transcription
                    // -------------------------------------------------

                    show(
                        transcriptionSection
                    );


                    setText(
                        recordingStatus,
                        "Transcription completed successfully."
                    );


                    if (recordingStatus) {

                        recordingStatus.className =
                            "iv-recording-status success";
                    }


                    transcribeButton.textContent =
                        "✓ Transcribed";


                    // -------------------------------------------------
                    // Enable FIR generation
                    // -------------------------------------------------

                    if (generateButton) {

                        generateButton.disabled =
                            transcriptText.trim().length === 0;
                    }

                }
                catch (error) {

                    console.error(
                        "Transcription error:",
                        error
                    );


                    alert(
                        error.message ||
                        "Unable to transcribe the recording."
                    );


                    transcribeButton.disabled =
                        false;


                    transcribeButton.textContent =
                        "Transcribe Recording";


                    setText(
                        recordingStatus,
                        "Transcription failed."
                    );
                }
            }
        );
    }


    // =========================================================
    // GENERATE FIR
    // =========================================================

    if (generateButton) {

        generateButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                const transcriptText =
                    transcription
                        ? (
                            transcription.value ||
                            transcription.textContent ||
                            ""
                        ).trim()
                        : "";


                if (!transcriptText) {

                    alert(
                        "Please transcribe the complaint first."
                    );

                    return;
                }


                generateButton.disabled =
                    true;

                generateButton.textContent =
                    "Generating FIR...";


                setText(
                    generationStatus,
                    "AI Investigation Agent is analysing the complaint..."
                );


                try {

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
                                        transcriptText,

                                    complaint_text:
                                        transcriptText

                                })
                            }
                        );


                    const data =
                        await response.json();


                    console.log(
                        "FIR generation response:",
                        data
                    );


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            data.message ||
                            "FIR generation failed."
                        );
                    }


                    if (
                        data.success === false
                    ) {

                        throw new Error(
                            data.error ||
                            "FIR generation failed."
                        );
                    }


                    currentFirId =
                        data.fir_id ||
                        data.firId ||
                        data.fir?.fir_id ||
                        null;


                    const fir =
                        data.fir ||
                        data.draft ||
                        data;


                    currentFIR =
                        fir;


                    displayFIR(fir);


                    show(firSection);


                    setText(
                        generationStatus,
                        "FIR draft generated successfully."
                    );


                    generateButton.textContent =
                        "✓ FIR Generated";

                }
                catch (error) {

                    console.error(
                        "FIR generation error:",
                        error
                    );


                    alert(
                        error.message ||
                        "Unable to generate FIR."
                    );


                    generateButton.disabled =
                        false;

                    generateButton.textContent =
                        "Generate FIR";


                    setText(
                        generationStatus,
                        "FIR generation failed."
                    );
                }
            }
        );
    }


    // =========================================================
    // DISPLAY FIR
    // =========================================================

    function displayFIR(fir) {

        if (!fir) {
            return;
        }


        console.log(
            "Displaying FIR:",
            fir
        );


        const fieldMap = {

            firNumber:
                fir.fir_number ?? "",

            firDateTime:
                fir.fir_date_time_display ||
                fir.fir_date_time ||
                "",

            district:
                fir.district ?? "",

            policeStation:
                fir.police_station ?? "",

            year:
                fir.year ?? "",


            complainantName:
                fir.complainant_name ?? "",

            fatherName:
                fir.father_husband_name ?? "",

            nationality:
                fir.nationality ?? "",

            occupation:
                fir.occupation ?? "",

            mobile:
                fir.mobile_number ?? "",

            phone:
                fir.phone_number ?? "",

            address:
                fir.complainant_address ?? "",

            uid:
                fir.uid_number ?? "",

            passport:
                fir.passport_number ?? "",

            idDetails:
                fir.other_id_details ?? "",


            occurrenceDate:
                fir.occurrence_date ?? "",

            occurrenceTime:
                fir.occurrence_time ?? "",

            occurrenceDateTo:
                fir.occurrence_date_to ?? "",

            occurrenceTimeTo:
                fir.occurrence_time_to ?? "",

            occurrenceDay:
                fir.occurrence_day ?? "",

            timePeriod:
                fir.time_period ?? "",

            placeOfOccurrence:
                fir.place_of_occurrence ?? "",


            informationReceivedDate:
                fir.information_received_date ?? "",

            informationReceivedTime:
                fir.information_received_time ?? "",


            generalDiary:
                fir.general_diary_reference ?? "",

            inquest:
                fir.inquest_ud_case ?? "",


            accusedName:
                fir.accused_details ?? "",


            reasonForDelay:
                fir.reason_for_delay ?? "",


            propertyDescription:
                fir.property_details ?? "",

            totalPropertyValue:
                fir.total_property_value ?? "",


            firstInformationContents:
                fir.first_information_contents ?? "",

            actionTaken:
                fir.action_taken ?? "",


            crimeCategory:
                fir.crime_category ?? ""
        };


        // ---------------------------------------------------------
        // Populate fields
        // ---------------------------------------------------------

        Object.keys(fieldMap).forEach(
            function (id) {

                const element =
                    document.getElementById(id);


                if (!element) {
                    return;
                }


                const value =
                    fieldMap[id];


                if (
                    element.tagName === "INPUT" ||
                    element.tagName === "TEXTAREA" ||
                    element.tagName === "SELECT"
                ) {

                    if (
                        value !== null &&
                        value !== undefined &&
                        value !== ""
                    ) {

                        element.value =
                            value;
                    }

                }
                else {

                    element.textContent =
                        value !== null &&
                        value !== undefined
                            ? value
                            : "";
                }
            }
        );


        // ---------------------------------------------------------
        // ACT
        // ---------------------------------------------------------

        const actElement =
            document.getElementById("act");


        if (actElement) {

            const actValue =
                fir.act || "";


            if (
                actElement.tagName === "INPUT" ||
                actElement.tagName === "TEXTAREA"
            ) {

                actElement.value =
                    actValue;

            }
            else {

                actElement.textContent =
                    actValue;
            }
        }


        // ---------------------------------------------------------
        // SECTION
        // ---------------------------------------------------------

        const sectionElement =
            document.getElementById("section");


        if (sectionElement) {

            const sectionValue =
                fir.section || "";


            if (
                sectionElement.tagName === "INPUT" ||
                sectionElement.tagName === "TEXTAREA"
            ) {

                sectionElement.value =
                    sectionValue;

            }
            else {

                sectionElement.textContent =
                    sectionValue;
            }
        }


        // ---------------------------------------------------------
        // Missing information
        // ---------------------------------------------------------

        displayMissingInformation(
            fir.missing_information || []
        );
    }


    // =========================================================
    // MISSING INFORMATION
    // =========================================================

    function displayMissingInformation(
        missing
    ) {

        const box =
            document.getElementById(
                "missingInformationBox"
            );


        const list =
            document.getElementById(
                "missingInformationList"
            );


        if (!box || !list) {
            return;
        }


        list.innerHTML = "";


        let items = [];


        if (
            Array.isArray(missing)
        ) {

            items =
                missing;

        }
        else if (
            typeof missing === "string"
        ) {

            items =
                [missing];
        }


        if (!items.length) {

            hide(box);

            return;
        }


        items.forEach(
            function (item) {

                const li =
                    document.createElement(
                        "li"
                    );


                li.textContent =
                    item;


                list.appendChild(
                    li
                );
            }
        );


        show(box);
    }


    // =========================================================
    // COLLECT EDITABLE FIR FIELDS
    // =========================================================

    function collectEditableFields() {

        const data = {};


        const editableIds = [

            "occurrenceDay",
            "occurrenceDate",
            "occurrenceTime",
            "occurrenceDateTo",
            "occurrenceTimeTo",

            "timePeriod",
            "informationType",
            "generalDiary",
            "generalDiaryDateTime",

            "directionDistance",
            "beatNumber",

            "placeOfOccurrence",
            "outsidePoliceStation",
            "outsideDistrictState",

            "complainantName",
            "fatherName",
            "dateOfBirth",
            "nationality",

            "uid",
            "passport",
            "passportPlace",
            "passportDate",

            "idDetails",
            "idNumber",

            "address",
            "permanentAddress",
            "occupation",

            "phone",
            "mobile",

            "accusedName",
            "accusedAlias",
            "accusedRelative",
            "accusedAddress",

            "delayReason",

            "propertyCategory",
            "propertyType",
            "propertyDescription",
            "propertyValue",
            "totalPropertyValue",

            "inquest",

            "firstInformationContents",

            "investigationOfficer",
            "investigationOfficerRank",
            "investigationOfficerNumber",

            "actionTaken",

            "crimeCategory",

            "dispatchDateTime"
        ];


        editableIds.forEach(
            function (id) {

                const element =
                    document.getElementById(
                        id
                    );


                if (!element) {
                    return;
                }


                data[id] =
                    element.value ??
                    element.textContent ??
                    "";
            }
        );


        const actElement =
            document.getElementById(
                "act"
            );


        const sectionElement =
            document.getElementById(
                "section"
            );


        if (actElement) {

            data.act =
                actElement.value ??
                actElement.textContent ??
                "";
        }


        if (sectionElement) {

            data.section =
                sectionElement.value ??
                sectionElement.textContent ??
                "";
        }


        return data;
    }


    // =========================================================
    // APPROVE FIR
    // =========================================================

    if (approveButton) {

        approveButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                if (!currentFirId) {

                    alert(
                        "FIR draft ID is missing."
                    );

                    return;
                }


                const confirmation =
                    confirm(
                        "Are you sure you want to approve this FIR?"
                    );


                if (!confirmation) {
                    return;
                }


                approveButton.disabled =
                    true;


                if (rejectButton) {

                    rejectButton.disabled =
                        true;
                }


                setText(
                    reviewStatus,
                    "Approving FIR..."
                );


                try {

                    const editableData =
                        collectEditableFields();


                    const response =
                        await fetch(
                            "/fir/approve/" +
                            currentFirId,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    editable_data:
                                        editableData
                                })
                            }
                        );


                    const data =
                        await response.json();


                    console.log(
                        "Approval response:",
                        data
                    );


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            data.message ||
                            "FIR approval failed."
                        );
                    }


                    if (
                        data.success === false
                    ) {

                        throw new Error(
                            data.error ||
                            "FIR approval failed."
                        );
                    }


                    const approval =
                        data.approval ||
                        data.result ||
                        data;


                    displayFinalFIR(
                        currentFIR,
                        approval
                    );


                    show(finalSection);

                    hide(approveButton);

                    hide(rejectButton);


                    setText(
                        reviewStatus,
                        "FIR approved successfully."
                    );

                }
                catch (error) {

                    console.error(
                        "Approval error:",
                        error
                    );


                    alert(
                        error.message ||
                        "Unable to approve FIR."
                    );


                    approveButton.disabled =
                        false;


                    if (rejectButton) {

                        rejectButton.disabled =
                            false;
                    }


                    setText(
                        reviewStatus,
                        "Approval failed."
                    );
                }
            }
        );
    }


    // =========================================================
    // REJECT FIR
    // =========================================================

    if (rejectButton) {

        rejectButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                if (!currentFirId) {

                    alert(
                        "FIR draft ID is missing."
                    );

                    return;
                }


                const confirmation =
                    confirm(
                        "Reject this FIR draft and start a new complaint?"
                    );


                if (!confirmation) {
                    return;
                }


                rejectButton.disabled =
                    true;


                if (approveButton) {

                    approveButton.disabled =
                        true;
                }


                try {

                    const response =
                        await fetch(
                            "/fir/reject/" +
                            currentFirId,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    officer_remarks:
                                        "Draft rejected by officer."
                                })
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "FIR rejection failed."
                        );
                    }


                    alert(
                        "FIR draft rejected. Please record a NEW complaint."
                    );


                    // -------------------------------------------------
                    // Reset workflow
                    // -------------------------------------------------

                    currentComplaintId =
                        null;

                    currentFirId =
                        null;

                    currentFIR =
                        null;

                    recordedAudioBlob =
                        null;

                    audioChunks =
                        [];


                    if (transcription) {

                        transcription.value =
                            "";
                    }


                    hide(
                        transcriptionSection
                    );

                    hide(firSection);

                    hide(finalSection);


                    if (audioPlayer) {

                        audioPlayer.removeAttribute(
                            "src"
                        );

                        audioPlayer.load();
                    }


                    hide(audioPreview);


                    resetRecordingUI();


                    if (generateButton) {

                        generateButton.disabled =
                            true;

                        generateButton.textContent =
                            "Generate FIR";
                    }

                }
                catch (error) {

                    console.error(
                        "Reject error:",
                        error
                    );


                    alert(
                        error.message ||
                        "Unable to reject FIR."
                    );


                    rejectButton.disabled =
                        false;


                    if (approveButton) {

                        approveButton.disabled =
                            false;
                    }
                }
            }
        );
    }


    // =========================================================
    // DISPLAY FINAL FIR
    // =========================================================

    function displayFinalFIR(
        fir,
        approval
    ) {

        if (!fir) {
            fir = {};
        }


        if (!approval) {
            approval = {};
        }


        const finalFirNumber =
            approval.fir_number ||
            fir.fir_number ||
            "";


        const finalFirDateTime =
            approval.fir_date_time ||
            fir.fir_date_time ||
            "";


        const finalNumberElement =
            document.getElementById(
                "finalFirNumber"
            );


        const finalDateElement =
            document.getElementById(
                "finalFirDateTime"
            );


        if (finalNumberElement) {

            finalNumberElement.textContent =
                finalFirNumber;
        }


        if (finalDateElement) {

            finalDateElement.textContent =
                finalFirDateTime;
        }


        if (finalSection) {

            finalSection.style.display =
                "";
        }
    }


    // =========================================================
    // PRINT
    // =========================================================

    if (printButton) {

        printButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                window.print();
            }
        );
    }


    // =========================================================
    // INITIAL UI STATE
    // =========================================================

    if (recordButton) {

        recordButton.disabled =
            false;
    }


    if (stopButton) {

        stopButton.disabled =
            true;
    }


    if (transcribeButton) {

        transcribeButton.disabled =
            true;
    }


    if (generateButton) {

        generateButton.disabled =
            true;
    }


    hide(transcriptionSection);

    hide(firSection);

    hide(finalSection);


    console.log(
        "IntelliVision JavaScript loaded successfully."
    );

});