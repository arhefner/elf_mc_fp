            INCL    "1802.inc"

            ORG     $0000

            LBR     START
START:      GHI     R0
            PHI     R2
            LDI     LOW(BUF)
            PLO     R2
            SEX     R2
            BN4     $
            B4      $
            INP     4
            PHI     RD
            STR     R2
            OUT     4
            BN4     $
            B4      $
            INP     4
            PLO     RD
            STR     R2
            OUT     4
            SEX     RD
LOOP:       BN4     $
            B4      $
            INP     4
            OUT     4
            BR      LOOP
BUF:        DS      2

            END
