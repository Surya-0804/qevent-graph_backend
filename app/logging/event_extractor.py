from app.logging.event_schema import GateEvent, MeasurementEvent, Event

def extract_events(qc):
    events = []
    event_id = 0
    time = 0

    # Execution start
    events.append(Event(event_id, "EXECUTION_START", time))
    event_id += 1
    time += 1

    for instr in qc.data:
        op = instr.operation
        qubits = [qc.find_bit(q).index for q in instr.qubits]

        if op.name == "measure":
            clbits = [qc.find_bit(c).index for c in instr.clbits]
            events.append(
                MeasurementEvent(
                    event_id,
                    "MEASUREMENT",
                    time,
                    qubits,
                    clbits
                )
            )
        else:
            events.append(
                GateEvent(
                    event_id,
                    "GATE",
                    time,
                    op.name.upper(),
                    qubits
                )
            )

        event_id += 1
        time += 1

    # Execution end
    events.append(Event(event_id, "EXECUTION_END", time))

    return events
