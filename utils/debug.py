from odf.text import Span

def test_span():
    print("Type of Span:", type(Span))
    instance_check = isinstance(Span(), Span)
    print(f"Is Span() an instance of Span?: {instance_check}")

if __name__ == "__main__":
    test_span()
