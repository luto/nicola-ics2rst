# ice Shortag

This plugin provides the `ics` shorttag. It converts an ICS-calendar-file provided
via http(s) to an event list.

## Usage

```
{{% ics %}}https://somedomain.com/user/events.ics/{{% /ics %}}
```

Instead of the URL you can also supply a local file by specifying a `file://`-URL.

## Dependencies

A couple 3rd-party python modules are required. They can be installed using the
`pip3 install -r requirements.txt` command.
