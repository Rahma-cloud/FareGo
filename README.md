# FareGo

**Cashless shuttle payments for campus life.**

FareGo is a scan-to-pay web platform built for University of Ilorin campus
shuttle buses. Students pay their fare by scanning a driver's QR code, with no
cash and no manual bank transfers, and drivers get a clear record of their
daily earnings.

## The Problem

- Long queues at shuttle stops while students fumble for cash or wait for
  transfers to be confirmed
- Students without cash at hand when they board
- Manual bank transfers that are slow, error-prone, and hard to verify
- Little visibility for students on how much they spend on transport

## How It Works

1. Each driver has a unique QR code, printed as a sticker on their bus.
2. A student scans the code and pays the flat shuttle fare.
3. Both student and driver receive instant confirmation and a digital receipt.
4. FareGo tracks payments and turns them into spending and income insights.

## Features

- **Scan-to-pay:** QR-based fare payment at a flat fare price
- **AI-generated receipts and expense reports:** automatic records for every
  ride
- **Duplicate payment detection:** warns when a payment looks like a repeat,
  but still lets the student proceed (for example, when paying for a friend)
- **Weekly and monthly insights:** transport spending for students and income
  for drivers, helping budget-minded students plan ahead

## Who It's For

- **Students:** pay quickly, skip the cash hunt, and track transport spending
- **Drivers:** independent bus owners who want faster, verifiable payments
  and a clear view of their earnings

## Tech Stack

- **Frontend/App:** Streamlit
- **Database:** MySQL
- **Language:** Python
- **AI:** Claude, used for receipts, expense reports, and insights

## Project Status

In active development by a team of three. Requirements are documented in
[PRD.md](./PRD.md).

## Getting Started

_Installation and setup instructions coming soon._

## Contributing

_Contribution guidelines coming soon._
