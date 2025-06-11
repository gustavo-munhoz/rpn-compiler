#!/bin/bash

# Verifica se o número de argumentos é correto
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <EXPRESSIONS_FILE.txt>"
    exit 1
fi

INPUT_FILE="$1"

# --- ETAPA 1: Compilar o código fonte para Assembly usando Python ---
echo "Compiling with Python compiler..."
python3 main.py "$INPUT_FILE"

if [ $? -ne 0 ]; then
    echo "Error executing Python compiler (main.py)"
    exit 1
fi

BASE_NAME="${INPUT_FILE%.*}"
ASM_FILE="${BASE_NAME}.asm"
HEX_FILE="${BASE_NAME}.hex"
EXPECTED_RESULTS_FILE="${BASE_NAME}_expected.txt"

# --- ETAPA 2: Montar o Assembly para gerar o .hex ---
echo "Assembly generated."
echo "Assembling using avra to generate HEX: $HEX_FILE"

avra -o "$HEX_FILE" "$ASM_FILE"
if [ $? -ne 0 ]; then
    echo "Error assembling with avra."
    exit 1
fi

# --- ETAPA 3: Enviar o .hex para o Arduino ---
PORT="/dev/cu.usbserial-A5069RR4"
BAUD="57600"

echo "Uploading HEX to Arduino at port $PORT with baud rate $BAUD"
avrdude -v -patmega328p -carduino -P "$PORT" -b "$BAUD" -D -U flash:w:"$HEX_FILE":i

if [ $? -ne 0 ]; then
    echo "Error uploading HEX to Arduino."
    exit 1
fi

echo "Uploaded successfully!"

# --- ETAPA 4: Limpeza e Exibição de Resultados ---
echo "Cleaning build files..."

rm -f "${BASE_NAME}.obj" "${BASE_NAME}.eep.hex" "$HEX_FILE"

echo "Done!"
echo "----------------------------------"

if [ -f "$EXPECTED_RESULTS_FILE" ]; then
  echo "Expected results:"
  cat "$EXPECTED_RESULTS_FILE"
  echo ""
else
  echo "Expected results file not found ($EXPECTED_RESULTS_FILE)."
  echo "Skipping display of expected results."
fi

echo "----------------------------------"

exit 0
