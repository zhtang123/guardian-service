This repository contains a server implementation that provides the following functionalities:

1. Adding a record to the database, which includes address, guardian type, and guardian information.
2. Querying the guardians of a specific address.

POST IP:12001/guardian-wallet/email

```angular2html
[
    {
        "guardian": "0x8D486485de5B988E227F320dca0891A4dCFaA5AA",
        "type": "email",
        "info": "123456@gmail.com",
        "signature": "0xb3c3b5a58eb323f817cff10af67d2fedfd91adcb00a6336b8786d75caf2f011d09dd23d517cfb686f7cc6d5967ceb1d5459391289a12436eb631a7002d173acd1c"
    }
]
```

POST IP:12001/guardian-wallet/email/query
```angular2html
{
    "guardians": [
        "0x8D486485de5B988E227F320dca0891A4dCFaA5AA"
    ] //地址列表
}
```