from datetime import datetime


def get_time_f(time: datetime) -> str:
    return time.strftime("%H:%M:%S") + f".{time.microsecond// 100:04d}"


def get_duration_f(first_time: datetime, second_time: datetime) -> str:
    diff = second_time - first_time
    return str(diff).split(":")[-1] + " sec"


def format_statistics_as_html_table(
    time_of_asking_question,
    duration_text_answer,
    time_of_requesting_narration,
    duration_first_chunk_audio,
    duration_last_chunk_audio,
):
    table_html = f"""
    <div class="d-flex justify-content-center">
        <table class="table table-bordered table-striped table-hover">
            <thead class="thead-dark">
                <tr>
                    <th>Statistic</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Time of asking text-question from 4o-mini</td>
                    <td>{time_of_asking_question}</td>
                </tr>
                <tr>
                    <td>Text-answer received after</td>
                    <td>{duration_text_answer}</td>
                </tr>
                <tr>
                    <td>Time of requesting narration</td>
                    <td>{time_of_requesting_narration}</td>
                </tr>
                <tr>
                    <td>First chunk of audio was sent after</td>
                    <td>{duration_first_chunk_audio}</td>
                </tr>
                <tr>
                    <td>Last chunk of audio was sent after</td>
                    <td>{duration_last_chunk_audio}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    return table_html
